const { setupDOM } = require('./test_setup.js');

async function runCampaignJournalTests() {
    console.log("--- Starting Campaign Journal Tests ---");
    let window, document;

    try {
        ({ window, document } = await setupDOM());
        global.window = window; 
        global.document = document;
    } catch (e) {
        console.error("Error during JSDOM setup for Campaign Journal:", e.stack);
        process.exitCode = 1; // Indicate failure
        return;
    }

    const mockCampaign = {
        id: "testCampaign1",
        name: "My Test Campaign",
        trackers: { campaignJournal: [] },
        system: "D&D 5e"
    };
    if (window.dataManager) {
        window.dataManager.campaigns = [mockCampaign];
        window.dataManager.currentCampaignId = mockCampaign.id;
    } else {
        console.error("dataManager not found on window object after setup.");
        process.exitCode = 1; return;
    }
    if (!window.campaignJournal) {
        console.error("window.campaignJournal is not defined. Check script loading.");
        process.exitCode = 1; return;
    }


    const mockJournalEntryData = {
        sessionNumber: 1,
        sessionDate: '2024-01-01',
        sessionTitle: 'The Beginning',
        earlierEvents: '# Previous Events', // Markdown content
        plannedSummary: '## Plan for Today', // Markdown content
        notes: '_Additional notes here._' // Markdown content
    };
    
    // Test renderCampaignJournalFormModal
    console.log("\nTesting window.campaignJournal.renderCampaignJournalFormModal invocation...");
    global.simpleMDEMockInstances = []; 
    let formModalError = false;
    try {
        // This function *should* call new SimpleMDE() for the textareas.
        window.campaignJournal.renderCampaignJournalFormModal(mockCampaign, null); 
        
        if (global.simpleMDEMockInstances.length === 3) {
            console.log("SUCCESS: SimpleMDE constructor was called 3 times for journal form.");
        } else {
            console.error(`FAILURE: Expected 3 SimpleMDE constructor calls for journal form, got ${global.simpleMDEMockInstances.length}.`);
            formModalError = true;
        }
        const cancelButton = document.getElementById('cancelJournalFormBtn');
        if (cancelButton) cancelButton.click();

    } catch (e) {
        console.error("Error during window.campaignJournal.renderCampaignJournalFormModal call:", e.stack || e);
        formModalError = true;
    }
    
    // Test renderCampaignJournalEntryView
    console.log("\nTesting window.campaignJournal.renderCampaignJournalEntryView invocation...");
    global.markedMockLog.calls = 0; 
    let entryViewError = false;
    try {
        // This function, in the *current version of the code being tested*,
        // uses escapeHtml, NOT marked.parse().
        window.campaignJournal.renderCampaignJournalEntryView(mockJournalEntryData, mockCampaign, 0);
        
        if (global.markedMockLog.calls === 0) {
            console.log(`SUCCESS: marked.parse was called ${global.markedMockLog.calls} times for journal view (as expected for this code version).`);
        } else {
            console.error(`FAILURE: Expected 0 marked.parse calls for journal view (current code uses escapeHtml), got ${global.markedMockLog.calls}.`);
            entryViewError = true;
        }
    } catch (e) {
        console.error("Error during window.campaignJournal.renderCampaignJournalEntryView call:", e.stack || e);
        entryViewError = true;
    }

    if (formModalError || entryViewError) {
        process.exitCode = 1; 
    }
    console.log("--- Campaign Journal Tests Finished ---");
}

runCampaignJournalTests();
