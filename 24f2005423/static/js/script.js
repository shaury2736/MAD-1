/* ═══════════════════════════════════════════════════════════════════════════════════
   PlaceIITM – Campus Placement Portal | Main JavaScript
   ═══════════════════════════════════════════════════════════════════════════════════ */

// ─── Initialize on Page Load ─────────────────────────────────────────
document.addEventListener('DOMContentLoaded', function() {
    initializeDateDisplay();
});

// ─── Date Display in Topbar ─────────────────────────────────────────
function initializeDateDisplay() {
    const d = new Date();
    const el = document.getElementById('current-date');
    if (el) {
        el.textContent = d.toLocaleDateString('en-IN', {
            weekday: 'short',
            day: 'numeric',
            month: 'short',
            year: 'numeric'
        });
    }
}

// ─── Login Page: Role Tab Switching ─────────────────────────────────
function setRole(role, el) {
    document.getElementById('roleInput').value = role;
    document.querySelectorAll('.role-tab').forEach(t => t.classList.remove('active'));
    el.classList.add('active');
    document.getElementById('adminHint').style.display = role === 'admin' ? 'block' : 'none';
}

// ─── Utility Functions ──────────────────────────────────────────────
function showConfirmation(message) {
    return confirm(message);
}
