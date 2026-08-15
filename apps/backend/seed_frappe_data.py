"""
Miracle Birds — Frappe CRM Mock Data Seed Script
Inserts 50 realistic B2B customers (Frappe CRM format) with full AI scores,
plus workflows, meetings, and recommendations.

Run inside the backend container:
  docker exec mb_backend python seed_frappe_data.py

Or locally (with correct DATABASE_URL):
  PYTHONPATH=. DATABASE_URL=... python seed_frappe_data.py
"""

import asyncio
import os
import random
import uuid
from datetime import datetime, timezone, timedelta

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text

# ── Database URL ─────────────────────────────────────────────
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://miracle_birds_user:ashlin@mb_postgres:5432/miracle_birds"
)

# ── Sample Data ───────────────────────────────────────────────
COMPANIES = [
    "Tata Consultancy Services", "Infosys Ltd", "Wipro Technologies",
    "HCL Technologies", "Tech Mahindra", "Zomato", "Swiggy",
    "Razorpay", "Freshworks", "Zoho Corp", "BrowserStack",
    "Postman Inc", "Hasura", "Setu", "Niyo", "Jupiter Money",
    "Urban Company", "Meesho", "ShareChat", "Vedantu",
    "Unacademy", "CRED", "PhonePe", "Groww", "Zerodha",
    "Ola Cabs", "OYO Rooms", "MakeMyTrip", "PolicyBazaar", "Paytm",
    "InMobi", "Druva", "Darwinbox", "Leadsquared", "Capillary Tech",
    "Khatabook", "OKCredit", "FarEye", "Locus.sh", "Delhivery",
    "Flipkart", "Snapdeal", "BigBasket", "Nykaa", "Bewakoof",
    "CleverTap", "WebEngage", "MoEngage", "Netcore", "Kaleyra",
]

FIRST_NAMES = [
    "Arjun", "Priya", "Rahul", "Ananya", "Vikram", "Sneha", "Amit",
    "Pooja", "Rohan", "Divya", "Siddharth", "Nisha", "Karan", "Aisha",
    "Manish", "Riya", "Deepak", "Sonia", "Nikhil", "Meera",
    "Aditya", "Kavya", "Gaurav", "Lakshmi", "Suresh", "Tanya",
    "Rajesh", "Swati", "Vinay", "Anjali", "Harsh", "Simran",
    "Pranav", "Isha", "Kunal", "Preeti", "Akash", "Neha",
    "Sumit", "Ritika", "Varun", "Sunita", "Aarav", "Pallavi",
    "Rohit", "Kriti", "Sandeep", "Madhuri", "Tarun", "Bhavna",
]

LAST_NAMES = [
    "Sharma", "Patel", "Singh", "Kumar", "Gupta", "Joshi", "Mehta",
    "Shah", "Verma", "Nair", "Reddy", "Iyer", "Pillai", "Menon",
    "Chopra", "Malhotra", "Kapoor", "Bansal", "Agarwal", "Sinha",
]

TITLES = [
    "CTO", "VP of Engineering", "Head of Product", "Director of Sales",
    "Chief Revenue Officer", "VP of Marketing", "Director of Operations",
    "Engineering Manager", "Product Manager", "Account Executive",
    "CEO", "Co-founder & CTO", "Lead Developer", "Data Science Lead",
]

ACTION_TYPES = [
    "Schedule Upsell Call",
    "Send Churn Prevention Email",
    "Offer Loyalty Discount",
    "Assign Dedicated CSM",
    "Send Product Update Email",
    "Initiate Re-engagement Campaign",
    "Schedule Executive Business Review",
    "Trigger Onboarding Sequence",
    "Offer Free Training Session",
    "Enable Premium Feature Trial",
]

WORKFLOW_TEMPLATES = [
    {
        "name": "Churn Risk Alert",
        "description": "Notify CSM when customer churn probability exceeds 60%",
        "conditions": {"field": "churn_probability", "operator": "gt", "value": 0.6},
        "actions": [{"type": "notify_csm"}, {"type": "create_task", "title": "Follow up with at-risk customer"}],
        "is_active": True,
    },
    {
        "name": "Hot Lead Assignment",
        "description": "Auto-assign leads with score > 80 to senior sales reps",
        "conditions": {"field": "lead_score", "operator": "gt", "value": 80},
        "actions": [{"type": "assign_sales_rep", "tier": "senior"}, {"type": "send_email", "template": "hot_lead_welcome"}],
        "is_active": True,
    },
    {
        "name": "Low Health Score Follow-up",
        "description": "Trigger CSM outreach when health score drops below 50",
        "conditions": {"field": "health_score", "operator": "lt", "value": 50},
        "actions": [{"type": "send_email", "template": "health_recovery"}, {"type": "create_task"}],
        "is_active": True,
    },
    {
        "name": "New Customer Onboarding",
        "description": "Start onboarding sequence for new customers within 24h of signup",
        "conditions": {"field": "status", "operator": "eq", "value": "new"},
        "actions": [{"type": "enroll_onboarding_sequence"}, {"type": "send_welcome_email"}],
        "is_active": True,
    },
    {
        "name": "Renewal Reminder",
        "description": "Send renewal reminder 30 days before subscription expiry",
        "conditions": {"field": "days_to_renewal", "operator": "lt", "value": 30},
        "actions": [{"type": "send_renewal_email"}, {"type": "notify_account_manager"}],
        "is_active": False,
    },
]

SUMMARY_TEMPLATES = [
    "Customer expressed strong interest in the enterprise tier upgrade. Key concerns around pricing were addressed with competitive ROI analysis. Next step: prepare custom proposal by EOW.",
    "Technical sync to resolve Frappe CRM integration issues. Root cause identified as API rate limiting. Engineering team to deploy fix within 48 hours.",
    "QBR meeting covered 6-month metrics. Customer NPS improved from 32 to 67. Churn risk reduced significantly after onboarding improvements.",
    "Renewal negotiation completed. 2-year deal signed at $84,000 ARR. Upsell opportunity identified for analytics add-on.",
    "Initial discovery call. Customer comes from Salesforce and wants tighter AI analytics. Strong alignment with our product roadmap.",
]

ACTION_ITEMS_TEMPLATES = [
    ["Send competitive pricing comparison", "Prepare enterprise demo", "Loop in CRO for final negotiation"],
    ["Deploy API rate limit fix", "Schedule training session", "Share integration documentation"],
    ["Share NPS improvement case study", "Enable advanced analytics module", "Schedule next QBR in Q3"],
    ["Process contract renewal", "Set up enterprise account", "Schedule onboarding for new seats"],
    ["Send product roadmap deck", "Schedule technical deep dive", "Assign dedicated CSM"],
]

MEETING_SENTIMENTS = ["positive", "neutral", "positive", "positive", "neutral"]


async def seed():
    engine = create_async_engine(DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        # Get the demo tenant_id
        tenant_result = await session.execute(
            text("SELECT tenant_id FROM core.users WHERE email = 'demo@miraclebirds.ai' LIMIT 1")
        )
        tenant_row = tenant_result.fetchone()
        if not tenant_row:
            print("ERROR: Demo user not found. Please register demo@miraclebirds.ai first.")
            return

        tenant_id = tenant_row[0]
        print(f"Found demo tenant: {tenant_id}")

        # ── 1. Seed 50 Customers ─────────────────────────────
        print("Seeding 50 Frappe CRM customers...")
        statuses = ["active"] * 28 + ["at_risk"] * 10 + ["trial"] * 7 + ["new"] * 3 + ["churned"] * 2
        customer_ids = []

        for i in range(50):
            cid = uuid.uuid4()
            customer_ids.append(cid)
            fname = FIRST_NAMES[i]
            lname = random.choice(LAST_NAMES)
            company = COMPANIES[i]
            title = random.choice(TITLES)
            status = statuses[i]

            if status in ("at_risk", "churned"):
                churn_prob = round(random.uniform(0.55, 0.92), 2)
                health_score = round(random.uniform(20, 50), 1)
                lead_score = random.randint(20, 55)
                lifetime_value = round(random.uniform(2000, 15000), 2)
            elif status == "trial":
                churn_prob = round(random.uniform(0.2, 0.5), 2)
                health_score = round(random.uniform(55, 75), 1)
                lead_score = random.randint(55, 80)
                lifetime_value = round(random.uniform(500, 3000), 2)
            elif status == "new":
                churn_prob = round(random.uniform(0.1, 0.3), 2)
                health_score = round(random.uniform(60, 80), 1)
                lead_score = random.randint(65, 90)
                lifetime_value = round(random.uniform(1000, 5000), 2)
            else:
                churn_prob = round(random.uniform(0.02, 0.35), 2)
                health_score = round(random.uniform(65, 98), 1)
                lead_score = random.randint(60, 98)
                lifetime_value = round(random.uniform(5000, 120000), 2)

            external_id = f"CUST-{1000 + i:04d}" if status in ("active", "at_risk", "churned") else f"LEAD-{2000 + i:04d}"
            email = f"{fname.lower()}.{lname.lower()}@{company.lower().replace(' ', '').replace('.', '')[:20]}.com"
            attrs = f'{{"industry": "SaaS", "employees": {random.choice([10, 50, 200, 500, 1000, 5000])}, "crm_import": "frappe", "region": "India"}}'
            created = datetime.now(timezone.utc) - timedelta(days=random.randint(1, 365))
            updated = datetime.now(timezone.utc) - timedelta(days=random.randint(0, 30))
            phone = f"+91 98{random.randint(10000000, 99999999)}"

            await session.execute(text("""
                INSERT INTO customers.customers (
                    id, tenant_id, external_id, crm_source,
                    first_name, last_name, email, phone, company, title,
                    status, health_score, churn_probability, lead_score, lifetime_value,
                    attributes, is_deleted, created_at, updated_at
                ) VALUES (
                    :id, :tenant_id, :external_id, :crm_source,
                    :first_name, :last_name, :email, :phone, :company, :title,
                    :status, :health_score, :churn_probability, :lead_score, :lifetime_value,
                    CAST(:attributes AS jsonb), false, :created_at, :updated_at
                ) ON CONFLICT DO NOTHING
            """), {
                "id": cid, "tenant_id": tenant_id,
                "external_id": external_id, "crm_source": "frappe",
                "first_name": fname, "last_name": lname,
                "email": email, "phone": phone,
                "company": company, "title": title, "status": status,
                "health_score": health_score, "churn_probability": churn_prob,
                "lead_score": lead_score, "lifetime_value": lifetime_value,
                "attributes": attrs,
                "created_at": created, "updated_at": updated,
            })

        print(f"  Seeded {len(customer_ids)} customers")

        # ── 2. Seed 5 Workflows ─────────────────────────────
        print("Seeding 5 workflow automations...")
        import json
        for wf in WORKFLOW_TEMPLATES:
            await session.execute(text("""
                INSERT INTO workflows.workflows (
                    id, tenant_id, name, description, conditions, actions, is_active, created_at, updated_at
                ) VALUES (
                    :id, :tenant_id, :name, :description,
                    CAST(:conditions AS jsonb), CAST(:actions AS jsonb),
                    :is_active, :created_at, :updated_at
                ) ON CONFLICT DO NOTHING
            """), {
                "id": uuid.uuid4(), "tenant_id": tenant_id,
                "name": wf["name"], "description": wf["description"],
                "conditions": json.dumps(wf["conditions"]),
                "actions": json.dumps(wf["actions"]),
                "is_active": wf["is_active"],
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc),
            })
        print("  Seeded 5 workflows")

        # ── 3. Seed 20 Meeting Summaries ────────────────────
        print("Seeding 20 meeting summaries...")
        meeting_customers = random.sample(customer_ids, min(20, len(customer_ids)))
        for j, cid in enumerate(meeting_customers):
            idx = j % len(SUMMARY_TEMPLATES)
            await session.execute(text("""
                INSERT INTO ai.meeting_summaries (
                    id, tenant_id, customer_id, transcript_summary,
                    action_items, sentiment, created_at, updated_at
                ) VALUES (
                    :id, :tenant_id, :customer_id, :transcript_summary,
                    CAST(:action_items AS jsonb), :sentiment, :created_at, :updated_at
                ) ON CONFLICT DO NOTHING
            """), {
                "id": uuid.uuid4(), "tenant_id": tenant_id, "customer_id": cid,
                "transcript_summary": SUMMARY_TEMPLATES[idx],
                "action_items": json.dumps(ACTION_ITEMS_TEMPLATES[idx]),
                "sentiment": MEETING_SENTIMENTS[idx],
                "created_at": datetime.now(timezone.utc) - timedelta(days=random.randint(0, 60)),
                "updated_at": datetime.now(timezone.utc),
            })
        print("  Seeded 20 meeting summaries")

        # ── 4. Seed 30 Recommendations ──────────────────────
        print("Seeding 30 AI recommendations...")
        rec_customers = random.sample(customer_ids, min(30, len(customer_ids)))
        statuses_rec = ["Pending"] * 15 + ["Accepted"] * 10 + ["Rejected"] * 5
        for k, cid in enumerate(rec_customers):
            action = ACTION_TYPES[k % len(ACTION_TYPES)]
            exp_rev = round(random.uniform(1000, 50000), 2)
            reason = (
                f"Customer engagement signals and historical purchase patterns indicate "
                f"{action.lower()} will yield ${exp_rev:,.0f} in incremental ARR."
            )
            await session.execute(text("""
                INSERT INTO ai.recommendations (
                    id, tenant_id, customer_id, type, confidence, expected_revenue,
                    status, business_reason, created_at, updated_at
                ) VALUES (
                    :id, :tenant_id, :customer_id, :type, :confidence, :expected_revenue,
                    :status, :business_reason, :created_at, :updated_at
                ) ON CONFLICT DO NOTHING
            """), {
                "id": uuid.uuid4(), "tenant_id": tenant_id, "customer_id": cid,
                "type": action,
                "confidence": round(random.uniform(0.65, 0.98), 2),
                "expected_revenue": exp_rev,
                "status": statuses_rec[k],
                "business_reason": reason,
                "created_at": datetime.now(timezone.utc) - timedelta(days=random.randint(0, 30)),
                "updated_at": datetime.now(timezone.utc),
            })
        print("  Seeded 30 recommendations")

        await session.commit()
        print("\nAll mock data seeded successfully!")
        print("  50 Frappe CRM customers (crm_source=frappe)")
        print("  5 workflow automations")
        print("  20 meeting summaries")
        print("  30 AI recommendations")
        print("\nLogin: http://localhost:13000/login")
        print("Email: demo@miraclebirds.ai | Password: Demo@123456")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed())
