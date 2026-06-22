# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from space_structure_generator_base import *  # noqa: F403,E402


TEAM_TYPE_SECTIONS = {
    "engineering": [
        {
            "title": "Architecture",
            "description": "System architecture, design decisions, and technical standards",
            "labels": ["architecture", "technical"],
            "children": [
                {"title": "Architecture Decision Records", "labels": ["adr", "decisions"]},
                {"title": "System Design Documents", "labels": ["design", "system"]},
                {"title": "API Documentation", "labels": ["api", "reference"]},
                {"title": "Tech Stack", "labels": ["tech-stack"]},
            ],
        },
        {
            "title": "Development",
            "description": "Development workflows, coding standards, and CI/CD",
            "labels": ["development"],
            "children": [
                {"title": "Coding Standards", "labels": ["standards", "code"]},
                {"title": "Git Workflow", "labels": ["git", "workflow"]},
                {"title": "CI/CD Pipeline", "labels": ["ci-cd", "devops"]},
                {"title": "Environment Setup", "labels": ["environment", "setup"]},
            ],
        },
        {
            "title": "Runbooks",
            "description": "Operational runbooks and incident response",
            "labels": ["runbooks", "operations"],
            "children": [
                {"title": "Incident Response", "labels": ["incident", "response"]},
                {"title": "Deployment Procedures", "labels": ["deployment"]},
                {"title": "Troubleshooting Guides", "labels": ["troubleshooting"]},
            ],
        },
    ],
    "product": [
        {
            "title": "Strategy",
            "description": "Product vision, roadmap, and strategic planning",
            "labels": ["strategy", "product"],
            "children": [
                {"title": "Product Vision", "labels": ["vision"]},
                {"title": "Roadmap", "labels": ["roadmap"]},
                {"title": "OKRs & Goals", "labels": ["okr", "goals"]},
                {"title": "Competitive Analysis", "labels": ["competitive", "analysis"]},
            ],
        },
        {
            "title": "Research",
            "description": "User research, personas, and market analysis",
            "labels": ["research"],
            "children": [
                {"title": "User Personas", "labels": ["personas"]},
                {"title": "User Interview Notes", "labels": ["interviews", "research"]},
                {"title": "Survey Results", "labels": ["surveys"]},
                {"title": "Usability Testing", "labels": ["usability", "testing"]},
            ],
        },
        {
            "title": "Requirements",
            "description": "Product requirements and feature specifications",
            "labels": ["requirements", "specs"],
            "children": [
                {"title": "Feature Specifications", "labels": ["features", "specs"]},
                {"title": "User Stories", "labels": ["user-stories"]},
                {"title": "Acceptance Criteria", "labels": ["acceptance-criteria"]},
            ],
        },
    ],
    "marketing": [
        {
            "title": "Strategy",
            "description": "Marketing strategy, brand guidelines, and campaign plans",
            "labels": ["strategy", "marketing"],
            "children": [
                {"title": "Brand Guidelines", "labels": ["brand", "guidelines"]},
                {"title": "Marketing Plan", "labels": ["plan"]},
                {"title": "Target Audiences", "labels": ["audience", "targeting"]},
                {"title": "Channel Strategy", "labels": ["channels"]},
            ],
        },
        {
            "title": "Campaigns",
            "description": "Active and past campaign documentation",
            "labels": ["campaigns"],
            "children": [
                {"title": "Active Campaigns", "labels": ["active"]},
                {"title": "Campaign Results", "labels": ["results", "analytics"]},
                {"title": "Campaign Templates", "labels": ["templates"]},
            ],
        },
        {
            "title": "Content",
            "description": "Content calendar, assets, and style guides",
            "labels": ["content"],
            "children": [
                {"title": "Content Calendar", "labels": ["calendar"]},
                {"title": "Content Assets", "labels": ["assets"]},
                {"title": "Style Guide", "labels": ["style-guide"]},
            ],
        },
    ],
    "project": [
        {
            "title": "Project Overview",
            "description": "Project charter, scope, and stakeholders",
            "labels": ["project", "overview"],
            "children": [
                {"title": "Project Charter", "labels": ["charter"]},
                {"title": "Scope & Deliverables", "labels": ["scope", "deliverables"]},
                {"title": "Stakeholder Map", "labels": ["stakeholders"]},
                {"title": "Timeline & Milestones", "labels": ["timeline", "milestones"]},
            ],
        },
        {
            "title": "Status & Reporting",
            "description": "Project status updates and reports",
            "labels": ["status", "reporting"],
            "children": [
                {"title": "Weekly Status Reports", "labels": ["status", "weekly"]},
                {"title": "Risk Register", "labels": ["risks"]},
                {"title": "Decision Log", "labels": ["decisions"]},
            ],
        },
        {
            "title": "Resources",
            "description": "Project resources, documentation, and references",
            "labels": ["resources"],
            "children": [
                {"title": "Technical Documentation", "labels": ["technical", "docs"]},
                {"title": "Vendor Information", "labels": ["vendor"]},
                {"title": "Budget & Financials", "labels": ["budget"]},
            ],
        },
    ],
}
