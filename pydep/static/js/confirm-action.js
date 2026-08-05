(function () {
    'use strict';

    const modalEl = document.getElementById('pydepConfirmModal');
    if (!modalEl || !window.bootstrap) {
        return;
    }

    const modal = bootstrap.Modal.getOrCreateInstance(modalEl);
    const titleEl = document.getElementById('pydepConfirmTitle');
    const messageEl = document.getElementById('pydepConfirmMessage');
    const iconEl = document.getElementById('pydepConfirmIcon');
    const okBtn = document.getElementById('pydepConfirmOk');
    let pendingForm = null;

    const variantClasses = {
        danger: 'confirm-modal__icon--danger',
        warning: 'confirm-modal__icon--warning',
        primary: 'confirm-modal__icon--primary',
    };

    const okClasses = {
        danger: 'btn-danger',
        warning: 'btn-warning',
        primary: 'btn-primary',
    };

    function setIconVariant(variant) {
        iconEl.className = 'confirm-modal__icon ' + (variantClasses[variant] || variantClasses.danger);
        const icons = {
            danger: 'bi-trash3',
            warning: 'bi-x-circle',
            primary: 'bi-question-circle',
        };
        iconEl.innerHTML = '<i class="bi ' + (icons[variant] || icons.danger) + '"></i>';
    }

    function openConfirm(btn) {
        pendingForm = btn.closest('form');
        if (!pendingForm && btn.dataset.confirmForm) {
            pendingForm = document.getElementById(btn.dataset.confirmForm);
        }
        if (!pendingForm) {
            return;
        }

        const variant = btn.dataset.confirmVariant || 'danger';
        titleEl.textContent = btn.dataset.confirmTitle || 'Подтвердите действие';
        messageEl.textContent = btn.dataset.confirmMessage || 'Вы уверены?';
        okBtn.textContent = btn.dataset.confirmOk || 'Подтвердить';
        okBtn.className = 'btn ' + (okClasses[variant] || okClasses.danger);
        setIconVariant(variant);
        modal.show();
    }

    document.addEventListener('click', function (event) {
        const btn = event.target.closest('[data-pydep-confirm]');
        if (!btn) {
            return;
        }
        event.preventDefault();
        openConfirm(btn);
    });

    okBtn.addEventListener('click', function () {
        if (pendingForm) {
            pendingForm.submit();
        }
        modal.hide();
    });

    modalEl.addEventListener('hidden.bs.modal', function () {
        pendingForm = null;
    });
})();
