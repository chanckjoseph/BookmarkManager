
// Docs Sidebar Component
// Usage: Include this script and <nav id="sidebar-container"></nav> in your HTML.

const SIDEBAR_CONFIG = [
    {
        title: "Docs Hub",
        path: "/home/joseph/Desktop/Antigravity/Bookmark Manager/docs/index.html",
        isHeader: true
    },
    {
        category: "Architecture",
        links: [
            { text: "Implementation Plan", path: "/home/joseph/Desktop/Antigravity/Bookmark Manager/docs/arch/plan.html" },
            { text: "Sync Logic Spec", path: "/home/joseph/Desktop/Antigravity/Bookmark Manager/docs/arch/sync_logic.html" }
        ]
    },
    {
        category: "Team & Process",
        links: [
            { text: "Multi-Agent Workflow", path: "/home/joseph/Desktop/Antigravity/Bookmark Manager/docs/process/workflow.html" }
        ]
    },
    {
        category: "History & Sprints",
        links: [
            { text: "Sprint 01: Feasibility", path: "/home/joseph/Desktop/Antigravity/Bookmark Manager/docs/sprints/sprint-01/index.html" },
            { text: "Sprint 02: MVP Core", path: "/home/joseph/Desktop/Antigravity/Bookmark Manager/docs/sprints/sprint-02/index.html" },
            { text: "Sprint 03: Persistence", path: "/home/joseph/Desktop/Antigravity/Bookmark Manager/docs/sprints/sprint-03/index.html" }
        ]
    },
    {
        category: "Source of Truth (Brain)",
        links: [
            { text: "Plan (MD)", path: "/home/joseph/.gemini/antigravity/brain/b5ee6891-816f-464e-a767-b78c5cc23fbf/implementation_plan.md" },
            { text: "Workflow (MD)", path: "/home/joseph/.gemini/antigravity/brain/b5ee6891-816f-464e-a767-b78c5cc23fbf/multi_agent_workflow.md" },
            { text: "Tasks (MD)", path: "/home/joseph/.gemini/antigravity/brain/b5ee6891-816f-464e-a767-b78c5cc23fbf/task.md" }
        ]
    }
];

function renderSidebar() {
    const container = document.querySelector('.sidebar');
    if (!container) return;

    let html = '';

    SIDEBAR_CONFIG.forEach(item => {
        if (item.isHeader && item.title) {
            html += `<h1><a href="${item.path}" style="color:white; text-decoration:none;">${item.title}</a></h1>`;
        } else if (item.category) {
            html += `<h3>${item.category}</h3><ul>`;
            item.links.forEach(link => {
                // Highlight active link
                const isActive = window.location.href.includes(link.path);
                const activeClass = isActive ? 'style="font-weight:700; color:var(--accent-color);"' : '';
                html += `<li><a href="${link.path}" ${activeClass}>${link.text}</a></li>`;
            });
            html += `</ul>`;
        }
    });

    container.innerHTML = html;
}

document.addEventListener('DOMContentLoaded', renderSidebar);
