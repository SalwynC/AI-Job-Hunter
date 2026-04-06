#!/usr/bin/env python3
"""
Telegram Bot for AI Job Hunter
==============================

Delivers job updates, handles queries, and provides career assistance via Telegram.
- Instant cached database queries
- Interactive inline buttons for job tracking
- Smart Gemini-powered chat for natural language queries
- On-demand /fetch command for real-time scraping
"""

import os
import json
import logging
import asyncio
import re
from datetime import datetime, timezone
from typing import List, Dict, Optional
from pathlib import Path

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, Bot
from telegram.ext import (
    Application, CommandHandler, MessageHandler, filters,
    ContextTypes, CallbackQueryHandler
)
from telegram.constants import ChatAction, ParseMode

import pandas as pd
from config.role_loader import load_role_profiles

# Database imports
from database.engine import engine
from database.models import JobArchive, TrackedApplication
from sqlalchemy.orm import Session
from sqlalchemy import desc, func

logger = logging.getLogger(__name__)

# Gemini client (lazy init)
_gemini_client = None

def get_gemini_client():
    """Lazy-initialize Gemini client."""
    global _gemini_client
    if _gemini_client is None:
        api_key = os.getenv("GEMINI_API_KEY", "")
        if api_key:
            try:
                from google import genai
                _gemini_client = genai.Client(api_key=api_key)
                logger.info("✅ Gemini AI client initialized")
            except Exception as e:
                logger.warning(f"Failed to init Gemini: {e}")
    return _gemini_client


def ask_gemini(prompt: str) -> Optional[str]:
    """Send a prompt to Gemini and return the response text."""
    client = get_gemini_client()
    if not client:
        return None
    try:
        response = client.models.generate_content(
            model='gemini-2.0-flash',
            contents=prompt
        )
        text = response.text.strip()
        # Ensure clean UTF-8 string (fixes ascii codec error)
        return text.encode('utf-8', errors='replace').decode('utf-8')
    except Exception as e:
        logger.error(f"Gemini error: {e}")
        return None


def escape_md(text: str) -> str:
    """Escape special Telegram Markdown characters to prevent 400 errors."""
    if not text:
        return ''
    # Replace markdown-breaking characters
    for ch in ['*', '_', '`', '[', ']', '(', ')', '~', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']:
        text = text.replace(ch, ' ')
    return text.strip()


class AIJobHunterBot:
    """Main Telegram bot handler for job delivery and queries."""
    
    def __init__(self, bot_token: str):
        self.bot_token = bot_token
        
    async def start_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /start command."""
        user = update.effective_user
        await update.message.reply_text(
            f"🚀 *Welcome to AI Job Hunter Bot!*\n\n"
            f"Hey {user.first_name}! I'm your AI-powered job hunting assistant for 2026 freshers.\n\n"
            f"📋 *Commands:*\n"
            f"/jobs — Top 10 highest-scoring jobs\n"
            f"/internships — Latest internship opportunities\n"
            f"/roles — List all tracked role categories\n"
            f"/stats — Database statistics\n"
            f"/fetch `role_name` — Scrape jobs for a role NOW\n"
            f"/apply `link` `company` — Track an application\n"
            f"/help — Full command list\n\n"
            f"💬 *Or just type naturally:*\n"
            f"• `data analyst jobs in bangalore`\n"
            f"• `how to prepare for SQL interview`\n"
            f"• `show me MERN stack internships`\n"
            f"• `career tips for freshers`",
            parse_mode=ParseMode.MARKDOWN
        )

    async def help_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /help command."""
        help_text = (
            "🆘 *AI Job Hunter Bot — Help*\n\n"
            "*Job Commands:*\n"
            "/jobs — Top 10 matching jobs\n"
            "/internships — Internship opportunities\n"
            "/roles — All tracked role categories\n"
            "/fetch `role` — Scrape a specific role now\n\n"
            "*Tracking Commands:*\n"
            "/apply `link` `company` — Mark as applied\n"
            "/stats — Database statistics\n\n"
            "*Smart Chat:*\n"
            "Just type anything! I can answer:\n"
            "• Job search queries (\"analyst jobs in Pune\")\n"
            "• Career advice (\"how to crack interviews\")\n"
            "• Skill tips (\"what SQL topics to learn\")\n"
            "• Resume help (\"improve my resume for data roles\")"
        )
        await update.message.reply_text(help_text, parse_mode=ParseMode.MARKDOWN)
        
    async def jobs_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /jobs command — send top 10 highest-scoring jobs."""
        await update.message.chat.send_action(ChatAction.TYPING)
        
        try:
            with Session(engine) as db:
                jobs = db.query(JobArchive).order_by(
                    desc(JobArchive.score)
                ).limit(10).all()
            
            if not jobs:
                await update.message.reply_text(
                    "❌ No jobs in database yet. Run the scraper first:\n"
                    "`python3 main.py --once`\n\n"
                    "Or use /fetch data\\_analyst to scrape a specific role.",
                    parse_mode=ParseMode.MARKDOWN
                )
                return
            
            await self._send_jobs_with_buttons(update.message.chat_id, jobs, "🔥 Top 10 Matching Jobs")
        except Exception as e:
            logger.error(f"Error in jobs handler: {e}", exc_info=True)
            await update.message.reply_text("⚠️ Error fetching jobs from database.")
    
    async def internships_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /internships command."""
        await update.message.chat.send_action(ChatAction.TYPING)
        
        try:
            with Session(engine) as db:
                internships = db.query(JobArchive).filter(
                    JobArchive.title.ilike('%intern%') |
                    JobArchive.role.ilike('%intern%') |
                    JobArchive.source.ilike('%internshala%')
                ).order_by(desc(JobArchive.score)).limit(10).all()
            
            if not internships:
                await update.message.reply_text("No internships found in the database yet.")
                return
            
            await self._send_jobs_with_buttons(update.message.chat_id, internships, "🎓 Internship Opportunities")
        except Exception as e:
            logger.error(f"Error in internships handler: {e}")
            await update.message.reply_text(f"Error: {str(e)}")

    async def roles_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /roles — show all available role categories with job counts."""
        await update.message.chat.send_action(ChatAction.TYPING)
        try:
            with Session(engine) as db:
                role_counts = db.query(
                    JobArchive.role, func.count(JobArchive.id)
                ).group_by(JobArchive.role).all()
            
            if not role_counts:
                roles_data, _ = load_role_profiles()
                role_list = "\n".join([f"• `{k}` — {v.get('display_name', k)}" for k, v in list(roles_data.items())[:25]])
                await update.message.reply_text(
                    f"📋 *Available Roles (no data scraped yet):*\n\n{role_list}\n\n"
                    f"Use `/fetch role_name` to scrape any of these.",
                    parse_mode=ParseMode.MARKDOWN
                )
                return
            
            lines = []
            for role, count in sorted(role_counts, key=lambda x: x[1], reverse=True):
                if role:
                    lines.append(f"• `{role}`: {count} jobs")
            
            msg = "📋 *Jobs in Database by Role:*\n\n" + "\n".join(lines[:25])
            await update.message.reply_text(msg, parse_mode=ParseMode.MARKDOWN)
        except Exception as e:
            await update.message.reply_text(f"Error: {str(e)}")

    async def fetch_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /fetch <role> — on-demand scraping for a specific role."""
        if not context.args:
            await update.message.reply_text(
                "Usage: `/fetch data_analyst`\n\nUse /roles to see available roles.",
                parse_mode=ParseMode.MARKDOWN
            )
            return
        
        role_name = context.args[0].lower().strip()
        await update.message.reply_text(f"⏳ Fetching fresh jobs for `{role_name}`... this may take 30-60 seconds.", parse_mode=ParseMode.MARKDOWN)
        await update.message.chat.send_action(ChatAction.TYPING)
        
        try:
            roles_data, default = load_role_profiles()
            if role_name not in roles_data:
                available = ", ".join(list(roles_data.keys())[:15])
                await update.message.reply_text(
                    f"❌ Role `{role_name}` not found.\n\nAvailable: {available}",
                    parse_mode=ParseMode.MARKDOWN
                )
                return
            
            # Build profile and run pipeline
            profile = dict(roles_data[role_name])
            profile["role_key"] = role_name
            profile["default_role"] = default
            
            from config.role_loader import validate_profile
            validate_profile(profile, role_name)
            
            from automation.hourly_scraper import JobPipeline
            pipeline = JobPipeline(profile)
            result = await asyncio.get_event_loop().run_in_executor(None, pipeline.run)
            
            new_jobs = result.get('new_jobs', 0)
            
            if new_jobs > 0:
                # Fetch the freshly saved jobs from DB
                with Session(engine) as db:
                    fresh = db.query(JobArchive).filter(
                        JobArchive.role == role_name
                    ).order_by(desc(JobArchive.scraped_at)).limit(10).all()
                
                await self._send_jobs_with_buttons(
                    update.message.chat_id, fresh,
                    f"🔥 {new_jobs} Fresh Jobs for {roles_data[role_name].get('display_name', role_name)}"
                )
            else:
                await update.message.reply_text(
                    f"No new jobs found for `{role_name}` right now. "
                    f"Previously scraped: {result.get('scraped_jobs', 0)} total.",
                    parse_mode=ParseMode.MARKDOWN
                )
        except Exception as e:
            logger.error(f"Fetch error: {e}", exc_info=True)
            await update.message.reply_text(f"❌ Scraping failed: {str(e)[:200]}")

    async def stats_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Show database statistics."""
        try:
            with Session(engine) as db:
                total_jobs = db.query(JobArchive).count()
                total_apps = db.query(TrackedApplication).count()
                role_count = db.query(func.count(func.distinct(JobArchive.role))).scalar()
                source_count = db.query(func.count(func.distinct(JobArchive.source))).scalar()
                
            stats = (
                "📊 *Database Statistics*\n\n"
                f"• Total Jobs Discovered: *{total_jobs}*\n"
                f"• Tracked Applications: *{total_apps}*\n"
                f"• Active Role Categories: *{role_count}*\n"
                f"• Data Sources Used: *{source_count}*\n\n"
                f"Gemini AI: {'✅ Active' if os.getenv('GEMINI_API_KEY') else '⚠️ Inactive'}"
            )
            await update.message.reply_text(stats, parse_mode=ParseMode.MARKDOWN)
        except Exception as e:
            await update.message.reply_text(f"Error: {str(e)}")

    async def apply_command_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /apply command — track an application."""
        if not context.args or len(context.args) < 2:
            await update.message.reply_text(
                "Usage: `/apply https://example.com/job CompanyName`",
                parse_mode=ParseMode.MARKDOWN
            )
            return

        job_link = context.args[0]
        company = ' '.join(context.args[1:])

        try:
            with Session(engine) as db:
                exist = db.query(TrackedApplication).filter(TrackedApplication.link == job_link).first()
                if not exist:
                    tracked = TrackedApplication(
                        link=job_link,
                        title="Manual via /apply",
                        company=company,
                        role="",
                        status="applied_via_bot"
                    )
                    db.add(tracked)
                    db.commit()
                    await update.message.reply_text(f"✅ Tracked! Marked as applied to *{company}*. Good luck 🍀", parse_mode=ParseMode.MARKDOWN)
                else:
                    await update.message.reply_text(f"ℹ️ Already tracking an application for *{company}*.", parse_mode=ParseMode.MARKDOWN)
        except Exception as e:
            logger.error(f"Apply error: {e}")
            await update.message.reply_text(f"Error: {str(e)}")

    async def chat_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle ANY free-form text — always responds."""
        if not update.message or not update.message.text:
            return

        user_message = update.message.text.strip()
        if not user_message:
            return
            
        await update.message.chat.send_action(ChatAction.TYPING)

        # Step 1: Try to find matching jobs in DB
        job_keywords = ['job', 'jobs', 'intern', 'internship', 'analyst', 'developer',
                        'engineer', 'fresher', 'opening', 'vacancy', 'hiring', 'role',
                        'mern', 'full stack', 'data', 'python', 'java', 'react', 'node',
                        'sql', 'frontend', 'backend', 'devops', 'cloud', 'ai', 'ml',
                        'web', 'django', 'flask', 'angular', 'vue', 'bi', 'mis',
                        'pune', 'bangalore', 'hyderabad', 'delhi', 'mumbai', 'chennai',
                        'remote', 'on-site', 'onsite', 'india']
        
        is_job_query = any(kw in user_message.lower() for kw in job_keywords)
        
        if is_job_query:
            try:
                with Session(engine) as db:
                    search_words = [w for w in user_message.lower().split() 
                                   if len(w) > 2 and w not in ('the', 'for', 'and', 'show', 'get', 'find', 'me', 'in', 'at', 'with', 'what', 'how', 'can', 'are', 'there', 'any')]
                    
                    if search_words:
                        # Use OR logic so broader matches work
                        from sqlalchemy import or_
                        conditions = []
                        for word in search_words[:4]:
                            term = f"%{word}%"
                            conditions.append(JobArchive.title.ilike(term))
                            conditions.append(JobArchive.company.ilike(term))
                            conditions.append(JobArchive.role.ilike(term))
                            conditions.append(JobArchive.location.ilike(term))
                        
                        matches = db.query(JobArchive).filter(
                            or_(*conditions)
                        ).order_by(desc(JobArchive.score)).limit(10).all()
                    else:
                        matches = db.query(JobArchive).order_by(desc(JobArchive.score)).limit(10).all()
                
                if matches:
                    await self._send_jobs_with_buttons(
                        update.message.chat_id, matches,
                        f"Results for: {user_message[:50]}"
                    )
                    return
            except Exception as e:
                logger.error(f"DB search error: {e}")

        # Step 2: Use Gemini AI for intelligent response (works for ANY question)
        gemini_response = ask_gemini(
            f"""You are an AI career assistant for a 2026 CSE graduate from India looking for fresher jobs and internships. You must be helpful and answer ANY question.

The user says: "{user_message}"

Rules:
- If about jobs/roles: give specific India-based role suggestions, salary ranges, and platforms
- If about interview tips: give practical advice with examples
- If about skills: recommend learning paths with FREE resources
- If about resume/cover letter: give actionable templates
- If it's a greeting (hi, hello): greet back warmly and list what you can help with
- If it's anything else: still answer helpfully as a career mentor
- Keep response under 300 words, practical, encouraging
- Use plain text only, no markdown formatting, no asterisks for bold
- Use emojis to make it friendly"""
        )
        
        if gemini_response:
            if len(gemini_response) > 4000:
                gemini_response = gemini_response[:3900] + "\n\n...(truncated)"
            
            try:
                # Always send as plain text to avoid 400 errors
                await update.message.reply_text(gemini_response)
            except Exception as e:
                logger.error(f"Reply error: {e}")
                await update.message.reply_text("Sorry, I had trouble processing that. Try again!")
        else:
            # Gemini unavailable — always give a helpful fallback
            await update.message.reply_text(
                f"I received your message: \"{user_message[:100]}\"\n\n"
                f"Here's what I can do:\n"
                f"/jobs - See top 10 matching jobs\n"
                f"/internships - Latest internships\n"
                f"/roles - All 40+ role categories\n"
                f"/fetch data_analyst - Scrape fresh jobs now\n"
                f"/stats - Database statistics\n\n"
                f"Or just ask me anything about careers, interviews, or job search!"
            )


    async def button_callback_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle interactive inline button clicks."""
        query = update.callback_query
        await query.answer()

        data = query.data
        if data.startswith("save_"):
            job_id_str = data.split("_")[1]
            try:
                with Session(engine) as db:
                    job = db.query(JobArchive).filter(JobArchive.id == int(job_id_str)).first()
                    if job:
                        exist = db.query(TrackedApplication).filter(TrackedApplication.link == job.link).first()
                        if not exist:
                            tracked = TrackedApplication(
                                link=job.link,
                                title=job.title,
                                company=job.company,
                                role=job.role,
                                status="applied_via_bot"
                            )
                            db.add(tracked)
                            db.commit()
                            await query.edit_message_text(
                                text=f"✅ *Applied!* {job.title} @ {job.company}\n🔗 {job.link}",
                                parse_mode=ParseMode.MARKDOWN
                            )
                        else:
                            await query.edit_message_text(
                                text=f"ℹ️ Already tracked: {job.title} @ {job.company}",
                                parse_mode=ParseMode.MARKDOWN
                            )
            except Exception as e:
                logger.error(f"Callback error: {e}")
                
        elif data.startswith("details_"):
            job_id_str = data.split("_")[1]
            try:
                with Session(engine) as db:
                    job = db.query(JobArchive).filter(JobArchive.id == int(job_id_str)).first()
                    if job:
                        raw = json.loads(job.raw_data) if job.raw_data else {}
                        desc_text = raw.get('description', 'No description available')[:800]
                        reqs = raw.get('requirements', '')[:300]
                        exp = raw.get('experience', 'Not specified')
                        
                        detail_msg = (
                            f"📋 *{job.title}*\n"
                            f"🏢 {job.company} | 📍 {job.location}\n"
                            f"💼 Experience: {exp}\n\n"
                            f"*Description:*\n{desc_text}\n"
                        )
                        if reqs:
                            detail_msg += f"\n*Requirements:*\n{reqs}"
                        
                        try:
                            await context.bot.send_message(
                                query.message.chat_id,
                                text=detail_msg[:4000],
                                parse_mode=ParseMode.MARKDOWN
                            )
                        except Exception:
                            await context.bot.send_message(
                                query.message.chat_id,
                                text=detail_msg[:4000]
                            )
            except Exception as e:
                logger.error(f"Details error: {e}")

    async def _send_jobs_with_buttons(self, chat_id: int, jobs: List[JobArchive], title: str = "🔥 Top Jobs") -> None:
        """Send jobs with clickable interactive buttons."""
        bot = Bot(token=self.bot_token)
        await bot.send_message(chat_id, f"*{title}*\n_{len(jobs)} results from database_", parse_mode=ParseMode.MARKDOWN)
        
        for job in jobs[:10]:
            try:
                score_val = job.score or 0
                score_emoji = "🔥" if score_val >= 8 else "⭐" if score_val >= 5 else "👍"
                
                raw = {}
                try:
                    raw = json.loads(job.raw_data) if job.raw_data else {}
                except:
                    pass
                    
                sal_text = raw.get('salary_text', 'Not disclosed')
                exp_text = raw.get('experience', 'Fresher')
                
                message = (
                    f"{score_emoji} {escape_md(job.title or 'Job')}\n"
                    f"Company: {escape_md(job.company or 'Unknown')}\n"
                    f"Location: {escape_md(job.location or 'India')}\n"
                    f"Exp: {escape_md(str(exp_text))} | Salary: {escape_md(str(sal_text))}\n"
                    f"Score: {score_val:.1f}/10\n"
                    f"Source: {escape_md(job.source or '')} | Role: {escape_md(job.role or 'General')}"
                )
                
                keyboard_layout = []
                if job.link:
                    keyboard_layout.append([InlineKeyboardButton("🔗 Apply Now", url=job.link)])
                    
                keyboard_layout.append([
                    InlineKeyboardButton("✅ Mark Applied", callback_data=f"save_{job.id}"),
                    InlineKeyboardButton("📋 Details", callback_data=f"details_{job.id}")
                ])
                
                keyboard = InlineKeyboardMarkup(keyboard_layout)
                try:
                    await bot.send_message(chat_id, message, reply_markup=keyboard)
                except Exception as e2:
                    logger.error(f"Send error: {e2}")
                await asyncio.sleep(0.3)
            except Exception as e:
                logger.error(f"Render error: {e}")


async def run_telegram_bot(bot_token: str):
    """Run the Telegram bot."""
    logger.info("🤖 Starting Telegram bot (Smart AI + Database Powered)...")
    
    bot = AIJobHunterBot(bot_token)
    app = Application.builder().token(bot_token).build()
    
    # Command handlers
    app.add_handler(CommandHandler("start", bot.start_handler))
    app.add_handler(CommandHandler("help", bot.help_handler))
    app.add_handler(CommandHandler("jobs", bot.jobs_handler))
    app.add_handler(CommandHandler("internships", bot.internships_handler))
    app.add_handler(CommandHandler("roles", bot.roles_handler))
    app.add_handler(CommandHandler("fetch", bot.fetch_handler))
    app.add_handler(CommandHandler("stats", bot.stats_handler))
    app.add_handler(CommandHandler("apply", bot.apply_command_handler))
    
    # Interactive button callbacks
    app.add_handler(CallbackQueryHandler(bot.button_callback_handler))
    
    # Smart free-form chat (must be last)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, bot.chat_handler))

    # Start polling
    await app.initialize()
    await app.start()
    await app.updater.start_polling(drop_pending_updates=True)
    
    logger.info("✅ Telegram bot is live! Send /start to your bot.")
    
    # Keep running until interrupted
    try:
        while True:
            await asyncio.sleep(1)
    except (KeyboardInterrupt, SystemExit):
        logger.info("Shutting down bot...")
        await app.updater.stop()
        await app.stop()
        await app.shutdown()


if __name__ == "__main__":
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN', '')
    if bot_token:
        asyncio.run(run_telegram_bot(bot_token))
    else:
        print("Set TELEGRAM_BOT_TOKEN env variable")
