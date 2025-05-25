// Modal utility for TTRPG Campaign Tracker
window.modalUtils = {
  modalInstance: null,

  initModal: function() {
    const modalElement = document.getElementById('genericModal');
    if (modalElement && typeof bootstrap !== 'undefined' && bootstrap.Modal) {
      this.modalInstance = new bootstrap.Modal(modalElement);
    } else {
      console.error('Modal element not found or Bootstrap Modal class not available at init.');
    }
  },

  showModal: function(title, bodyContent, footerContent = '') {
    if (!this.modalInstance) {
      this.initModal();
      if (!this.modalInstance) {
        console.error('Modal instance could not be initialized for showModal.');
        return;
      }
    }
    document.getElementById('genericModalLabel').textContent = title;
    document.getElementById('genericModalBody').innerHTML = bodyContent;
    document.getElementById('genericModalFooter').innerHTML = footerContent || '<button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>';
    const modalElement = document.getElementById('genericModal');
    if (modalElement) modalElement.removeAttribute('inert');
    this.modalInstance.show();
  },

  hideModal: function() {
    if (document.activeElement) document.activeElement.blur();
    const modalElement = document.getElementById('genericModal');
    if (modalElement) modalElement.setAttribute('inert', '');
    if (this.modalInstance) {
      this.modalInstance.hide();
    }
  },

  // Helper to escape HTML content before injecting
  escapeHtml: function(unsafe) {
    if (typeof unsafe !== 'string') return '';
    return unsafe
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
  },

  renderMarkdown: function(markdownString) {
    if (markdownString === null || typeof markdownString === 'undefined' || markdownString.trim() === '') {
      return '<div class="markdown-content">&nbsp;</div>';
    }
    // Assuming marked.parse() is available globally
    const parsedHtml = marked.parse(markdownString);
    return '<div class="markdown-content">' + parsedHtml + '</div>';
  },

  showConfirmModal: function(title, message, onConfirmCallback, onCancelCallback = null) {
    if (!this.modalInstance) {
      this.initModal();
      if (!this.modalInstance) {
        console.error('Modal instance could not be initialized for showConfirmModal.');
        // Fallback for critical confirmations if modal system fails
        if (confirm(message)) {
          if (onConfirmCallback) onConfirmCallback();
        } else {
          if (onCancelCallback) onCancelCallback();
        }
        return;
      }
    }

    const footerContent = `
      <button type="button" class="btn btn-secondary" id="modalCancelBtn">Cancel</button>
      <button type="button" class="btn btn-primary" id="modalConfirmBtn">Confirm</button>
    `;
    this.showModal(title, message, footerContent);

    let confirmClicked = false;
    const modalElement = document.getElementById('genericModal');
    const confirmButton = document.getElementById('modalConfirmBtn');
    const cancelButton = document.getElementById('modalCancelBtn');

    // Event listener cleanup and re-attachment using cloning
    const newConfirmButton = confirmButton.cloneNode(true);
    confirmButton.parentNode.replaceChild(newConfirmButton, confirmButton);
    
    const newCancelButton = cancelButton.cloneNode(true);
    cancelButton.parentNode.replaceChild(newCancelButton, cancelButton);

    newConfirmButton.addEventListener('click', () => {
      confirmClicked = true;
      if (onConfirmCallback) onConfirmCallback();
      this.hideModal();
    });

    newCancelButton.addEventListener('click', () => {
      if (onCancelCallback) onCancelCallback();
      this.hideModal(); // data-bs-dismiss might also handle this, but explicit call is safer
    });
    
    // Ensure data-bs-dismiss is present on the new cancel button if we rely on it
    newCancelButton.setAttribute('data-bs-dismiss', 'modal');


    const handleDismiss = () => {
      // Remove this listener to prevent multiple calls if modal is reshown
      modalElement.removeEventListener('hidden.bs.modal', handleDismiss);
      if (!confirmClicked && onCancelCallback) {
        onCancelCallback();
      }
    };
    modalElement.addEventListener('hidden.bs.modal', handleDismiss);
  },

  showAlertModal: function(title, message, onOkCallback = null) {
    if (!this.modalInstance) {
      this.initModal();
      if (!this.modalInstance) {
        console.error('Modal instance could not be initialized for showAlertModal.');
        // Fallback for critical alerts if modal system fails
        alert(message);
        if (onOkCallback) onOkCallback();
        return;
      }
    }

    const footerContent = `
      <button type="button" class="btn btn-primary" id="modalOkBtn">OK</button>
    `;
    this.showModal(title, message, footerContent);

    let okClicked = false; // To differentiate between OK click and other dismissals
    const modalElement = document.getElementById('genericModal');
    const okButton = document.getElementById('modalOkBtn');

    // Event listener cleanup and re-attachment
    const newOkButton = okButton.cloneNode(true);
    okButton.parentNode.replaceChild(newOkButton, okButton);

    newOkButton.addEventListener('click', () => {
      okClicked = true;
      if (onOkCallback) onOkCallback();
      this.hideModal();
    });

    // Ensure data-bs-dismiss is present on the new OK button if we rely on it
    newOkButton.setAttribute('data-bs-dismiss', 'modal');

    const handleDismiss = () => {
      modalElement.removeEventListener('hidden.bs.modal', handleDismiss);
      // For showAlertModal, onOkCallback is typically called regardless of how it's dismissed (OK, ESC, X)
      // unless okClicked was true (then it's already called).
      if (!okClicked && onOkCallback) {
        onOkCallback();
      }
    };
    modalElement.addEventListener('hidden.bs.modal', handleDismiss);
  }
};
