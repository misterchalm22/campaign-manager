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
  }
};
