// Data management for TTRPG Campaign Tracker
const CURRENT_SCHEMA_VERSION = "1.0.0";

window.dataManager = {
  loadCampaignsFromLocalStorage: function() {
    let rawData;
    try {
      rawData = localStorage.getItem('ttrpgCampaigns');
    } catch (error) {
      console.error("Error reading from localStorage:", error);
      let message = "Error loading data from local storage. Your browser's storage might be full or corrupted. Please try clearing your browser's cache for this site or contact support.";
      if (error.name === 'QuotaExceededError') {
        message = "Error loading data: Local storage quota exceeded. Please clear some space or contact support.";
      }
      // Assuming modalUtils is globally available
      if (window.modalUtils && typeof window.modalUtils.showErrorModal === 'function') {
        window.modalUtils.showErrorModal(message);
      } else {
        console.error("modalUtils.showErrorModal is not available. Message: " + message);
        alert(message); // Fallback
      }
      return {};
    }

    // Local Storage Capacity Check
    try {
      localStorage.setItem('__storage_test__', 'test');
      localStorage.removeItem('__storage_test__');
    } catch (error) {
      if (error.name === 'QuotaExceededError') {
        const message = "Local storage is full. The application may not function correctly. Please export your data and then clear some space by deleting old campaigns or browser data.";
        if (window.modalUtils && typeof window.modalUtils.showErrorModal === 'function') {
          window.modalUtils.showErrorModal(message);
        } else {
          console.error("modalUtils.showErrorModal is not available. Message: " + message);
          alert(message); // Fallback
        }
        // Depending on desired behavior, we might still return the data if it was retrieved before this check failed.
        // For now, we'll let it proceed to parse what was retrieved, if anything.
      }
    }

    let allCampaignData = {};
    if (rawData) {
      try {
        allCampaignData = JSON.parse(rawData);
      } catch (error) {
        console.error("Error parsing campaign data from localStorage:", error);
        // This specific error might indicate corrupted data rather than a storage issue.
        const message = "Error parsing stored data. It might be corrupted. If the problem persists, please try re-importing your data or contact support.";
         if (window.modalUtils && typeof window.modalUtils.showErrorModal === 'function') {
          window.modalUtils.showErrorModal(message);
        } else {
          console.error("modalUtils.showErrorModal is not available. Message: " + message);
          alert(message); // Fallback
        }
        return {}; // Return empty object if parsing fails
      }
    } else {
      // No data found, return empty object (or default structure)
      return {};
    }

    // Data Schema Versioning
    if (allCampaignData && typeof allCampaignData === 'object' && Object.keys(allCampaignData).length > 0) {
      if (allCampaignData.hasOwnProperty('_version')) {
        console.log("Loaded data schema version:", allCampaignData._version);
      } else {
        console.warn("Warning: Loaded campaign data is from an older version (pre-versioning). Consider exporting and re-importing your data to ensure compatibility with future updates.");
        allCampaignData._version = "0.9.0"; // Tentatively assign default old version
      }
    } else if (rawData) {
        // This case means rawData was not null, but parsed into a non-object or empty object.
        // This could happen if localStorage contained just "null" or "[]" or "{}"
        // For an empty object specifically, we might want to initialize it with a version.
        if (typeof allCampaignData === 'object' && Object.keys(allCampaignData).length === 0) {
            // It's an empty object, could be a fresh start or cleared data.
            // Let's not assign a version here, let save handle new data versioning.
            // Or, if we want to ensure even empty objects from storage get a version:
            // console.log("Initializing version for empty stored data object.");
            // allCampaignData._version = "0.9.0"; // Or current app version
        }
    }


    return allCampaignData;
  },
  saveCampaignsToLocalStorage: function(allCampaignData) {
    try {
      // Ensure allCampaignData is an object before stamping version
      if (typeof allCampaignData !== 'object' || allCampaignData === null) {
        console.error("Error: allCampaignData is not an object. Cannot set schema version.");
        // Optionally, show an error to the user or handle as appropriate
        // For now, we'll attempt to save it as is, but this indicates a problem elsewhere.
      } else {
        allCampaignData._version = CURRENT_SCHEMA_VERSION;
      }

      localStorage.setItem('ttrpgCampaigns', JSON.stringify(allCampaignData));
    } catch (error) {
      console.error("Error saving to localStorage:", error);
      let message = "Error: Failed to save data to local storage. An unexpected error occurred. Please try again. If the problem persists, you may need to export your data.";

      if (error.name === 'QuotaExceededError' || (error.code && (error.code === 22 || error.code === 1014)) || (error.number && error.number === -2147024882)) {
        // Note: Different browsers might throw different error codes/names for quota exceeded.
        // DOMException code 22 is common. Firefox might use NS_ERROR_DOM_QUOTA_REACHED.
        message = "Error: Could not save data. Local storage is full. Please export your existing data to create a backup, then consider deleting old or unneeded campaigns to free up space. No changes were saved.";
      }

      if (window.modalUtils && typeof window.modalUtils.showErrorModal === 'function') {
        window.modalUtils.showErrorModal(message);
      } else {
        console.error("modalUtils.showErrorModal is not available. Fallback message: " + message);
        alert(message); // Fallback
      }
      // The function should not propagate the error further.
    }
  },
  exportDataAsJSON: function(allCampaignData) {
    const dataStr = JSON.stringify(allCampaignData, null, 2);
    const blob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'ttrpg_campaigns.json';
    a.click();
    URL.revokeObjectURL(url);
  },
  handleJSONFileImport: function(file) {
    const reader = new FileReader();
    reader.onload = function(e) {
      let data;
      try {
        data = JSON.parse(e.target.result);
      } catch (err) {
        console.error("Error parsing JSON file:", err);
        const parseErrorMessage = "Import failed: The selected file is not valid JSON and could not be parsed.";
        if (window.modalUtils && typeof window.modalUtils.showErrorModal === 'function') {
          window.modalUtils.showErrorModal(parseErrorMessage);
        } else {
          // Fallback alert remains if modalUtils or showErrorModal is not available
          console.error("modalUtils.showErrorModal is not available. Fallback: " + parseErrorMessage);
          window.modalUtils.showAlertModal('Import Error', parseErrorMessage, null);
        }
        // Clear the file input for robustness, allowing re-selection of the same file if needed
        const fileInput = document.getElementById('import-file'); // Assuming 'import-file' is the ID of your file input
        if (fileInput) {
          fileInput.value = '';
        }
        return; // Stop further processing
      }

      // Data Structure Validation
      let isValidStructure = false;
      if (typeof data === 'object' && data !== null) {
        const campaignKeys = Object.keys(data);
        if (campaignKeys.length === 0 || data.hasOwnProperty('_version')) { 
          // Empty object is valid (could be an intentional reset or a new structure with just version)
          // Or if it only has a _version key (e.g. an empty dataset from a newer version)
          isValidStructure = true;
        } else {
          // Check if at least one campaign-like object exists
          for (const key of campaignKeys) {
            const campaign = data[key];
            if (typeof campaign === 'object' && campaign !== null &&
                typeof campaign.campaignName === 'string' &&
                typeof campaign.trackers === 'object' && campaign.trackers !== null) {
              isValidStructure = true;
              break; // Found one valid campaign structure, that's enough
            }
          }
        }
      }

      if (!isValidStructure) {
        const structureErrorMessage = "Import failed: The selected file does not appear to be a valid TTRPG campaign export. Its structure is incorrect.";
        if (window.modalUtils && typeof window.modalUtils.showErrorModal === 'function') {
          window.modalUtils.showErrorModal(structureErrorMessage);
        } else {
          // Fallback alert remains if modalUtils or showErrorModal is not available
          console.error("modalUtils.showErrorModal is not available. Fallback: " + structureErrorMessage);
          window.modalUtils.showAlertModal('Import Error', structureErrorMessage, null);
        }
        const fileInput = document.getElementById('import-file');
        if (fileInput) {
          fileInput.value = '';
        }
        return; // Stop further processing
      }

      // If validation passes
      try {
        localStorage.setItem('ttrpgCampaigns', JSON.stringify(data));
        const successMessage = "Import successful! Application will now reload.";
        if (window.modalUtils && typeof window.modalUtils.showInfoModal === 'function') {
          // Assuming showInfoModal might take a callback for after the modal is closed
          // If not, this will execute, then the modal will show, then reload.
          // For a truly blocking modal that needs user interaction before reload:
          // window.modalUtils.showInfoModal(successMessage, () => location.reload());
          // For now, using showAlertModal which is also blocking.
          // The original comment about 'alert' being "more reliably blocking" for reload
          // is addressed by showAlertModal also being a blocking modal.
          window.modalUtils.showAlertModal('Import Successful', successMessage, () => {
            location.reload();
          });
        } else {
          // This is the true fallback if modalUtils or showInfoModal is not available
          alert(successMessage);
          location.reload();
        }
      } catch (storageError) {
        // This catch block is for errors during localStorage.setItem, though it's less common here
        // if JSON.stringify succeeded. The QuotaExceededError is more likely.
        console.error("Error saving imported data to localStorage:", storageError);
        let storageErrorMessage = "Import failed: Could not save the imported data to local storage. ";
        if (storageError.name === 'QuotaExceededError') {
            storageErrorMessage += "Local storage is full. Please clear some space and try again.";
        } else {
            storageErrorMessage += "An unexpected error occurred."
        }

        if (window.modalUtils && typeof window.modalUtils.showErrorModal === 'function') {
          window.modalUtils.showErrorModal(storageErrorMessage);
        } else {
          // Fallback alert remains if modalUtils or showErrorModal is not available
          console.error("modalUtils.showErrorModal is not available. Fallback: " + storageErrorMessage);
          window.modalUtils.showAlertModal('Import Error', storageErrorMessage, null);
        }
        const fileInput = document.getElementById('import-file'); // Assuming 'import-file' is the ID of your file input
        if (fileInput) {
          fileInput.value = '';
        }
      }
    };
    reader.readAsText(file);
  }
};