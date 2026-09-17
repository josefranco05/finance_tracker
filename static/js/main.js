/* ============================================================
   MyFin · main.js
   - Mobile / tablet drawer (hamburger → sidebar + overlay)
   - Notifications popup (bell button)
   - Active nav-item highlight
   No dependencies. Loaded with `defer` from layout.html.
   ============================================================ */
(() => {
  'use strict';

  const body = document.body;
  const menuToggle = document.getElementById('menuToggle');
  const overlay = document.getElementById('overlay');
  const bellBtn = document.getElementById('bellBtn');
  const notifPanel = document.getElementById('notifPanel');
  const notifClose = document.getElementById('notifClose');
  const notifClear = document.getElementById('notifClear');
  const notifEmpty = document.getElementById('notifEmpty');
  const bellBadge = document.getElementById('bellBadge');

  /* ---------- 1. Active nav item ---------- */

  const setActiveNav = () => {
    const path = window.location.pathname;
    const key =
      path === '/' || path === '/home' ? 'home'
      : path.startsWith('/transactions') ? 'transactions'
      : path.startsWith('/dashboard') ? 'dashboard'
      : null;

    document.querySelectorAll('.nav-item').forEach((item) => {
      const isActive = item.dataset.nav === key;
      item.classList.toggle('active', isActive);
      if (isActive) {
        item.setAttribute('aria-current', 'page');
      } else {
        item.removeAttribute('aria-current');
      }
    });
  };

  /* ---------- 2. Sidebar drawer (tablet / phone) ---------- */

  const setNavOpen = (open) => {
    if (!menuToggle) return;
    body.classList.toggle('nav-open', open);
    if (overlay) overlay.hidden = !open;
    menuToggle.classList.toggle('active', open);
    menuToggle.setAttribute('aria-expanded', String(open));
    menuToggle.setAttribute('aria-label', open ? 'Cerrar menú' : 'Abrir menú');
  };

  if (menuToggle) {
    menuToggle.addEventListener('click', () => {
      setNavOpen(!body.classList.contains('nav-open'));
    });
  }

  if (overlay) {
    overlay.addEventListener('click', () => setNavOpen(false));
  }

  document.querySelectorAll('.nav-item').forEach((item) => {
    item.addEventListener('click', () => setNavOpen(false));
  });

  // If the window grows back to desktop size, reset the drawer state.
  window.addEventListener('resize', () => {
    if (window.matchMedia('(min-width: 1025px)').matches) {
      setNavOpen(false);
    }
  });

  /* ---------- 3. Notifications popup ---------- */

  const setNotifOpen = (open) => {
    if (!notifPanel || !bellBtn) return;
    notifPanel.hidden = !open;
    bellBtn.setAttribute('aria-expanded', String(open));
    if (open && notifClear) {
      notifClear.focus({ preventScroll: true });
    }
  };

  if (bellBtn && notifPanel) {
    bellBtn.addEventListener('click', (event) => {
      event.stopPropagation();
      setNotifOpen(notifPanel.hidden);
    });

    if (notifClose) {
      notifClose.addEventListener('click', () => setNotifOpen(false));
    }

    if (notifClear) {
      notifClear.addEventListener('click', () => {
        const items = document.querySelectorAll('#notifList .notif-item.unread');
        items.forEach((item) => {
          item.classList.remove('unread');
          const tag = item.querySelector('.notif-tag');
          if (tag) tag.remove();
        });
        if (bellBadge) bellBadge.hidden = true;
        if (notifEmpty && items.length > 0) notifEmpty.hidden = false;
        notifClear.disabled = true;
      });
    }

    // Clicking anywhere outside the panel (or the bell) closes it.
    document.addEventListener('pointerdown', (event) => {
      if (notifPanel.hidden) return;
      const insidePanel = notifPanel.contains(event.target);
      const onBell = bellBtn.contains(event.target);
      if (!insidePanel && !onBell) {
        setNotifOpen(false);
      }
    });
  }

  /* ---------- 4. Escape closes everything ---------- */

  document.addEventListener('keydown', (event) => {
    if (event.key !== 'Escape') return;
    if (notifPanel && !notifPanel.hidden) {
      setNotifOpen(false);
    }
    setNavOpen(false);
  });

  /* ---------- 5. Default date inputs to today (user's local date) ---------- */

  const setToday = (input) => {
    if (input.value) return;
    const now = new Date();
    const local = new Date(now.getTime() - now.getTimezoneOffset() * 60000);
    input.value = local.toISOString().slice(0, 10);
  };

  document.querySelectorAll('input[type="date"][data-today]').forEach(setToday);

  // after a form reset the date input clears — restore today again
  document.addEventListener('reset', (event) => {
    event.target.querySelectorAll('input[type="date"][data-today]').forEach(setToday);
  }, true);

  setActiveNav();
})();
