const { setupDOM } = require('./test_setup.js');

async function runNPCTrackerTests() {
    console.log("--- Starting NPC Tracker Tests ---");
    let window, document;

    try {
        ({ window, document } = await setupDOM());
        global.window = window; 
        global.document = document;
    } catch (e) {
        console.error("Error during JSDOM setup for NPC Tracker:", e.stack);
        process.exitCode = 1; // Indicate failure
        return;
    }
    
    const mockCampaign = {
        id: "testCampaignNPC",
        name: "My Test NPC Campaign",
        trackers: { npcs: [] },
        system: "Pathfinder 2e"
    };
    if (window.dataManager) {
        window.dataManager.campaigns = [mockCampaign];
        window.dataManager.currentCampaignId = mockCampaign.id;
    } else {
        console.error("dataManager not found on window object after setup.");
        process.exitCode = 1; return;
    }
    if (!window.npcTracker) {
        console.error("window.npcTracker is not defined. Check script loading.");
        process.exitCode = 1; return;
    }


    const mockNPCEntryData = {
        name: 'Goblin Boss',
        statBlock: 'Goblin',
        mmPage: '166',
        alterations: '## Alterations', // Markdown content
        alignment: 'NE',
        personality: '### Personality', // Markdown content
        appearance: '#### Appearance', // Markdown content
        secret: '**Secret**' // Markdown content
    };

    // Test renderNPCFormModal
    console.log("\nTesting window.npcTracker.renderNPCFormModal invocation...");
    global.simpleMDEMockInstances = []; 
    let formModalError = false;
    try {
        // This function *should* call new SimpleMDE() for the textareas.
        window.npcTracker.renderNPCFormModal(mockCampaign, null);
        
        if (global.simpleMDEMockInstances.length === 4) {
            console.log("SUCCESS: SimpleMDE constructor was called 4 times for NPC form.");
        } else {
            console.error(`FAILURE: Expected 4 SimpleMDE constructor calls for NPC form, got ${global.simpleMDEMockInstances.length}.`);
            formModalError = true;
        }
        const cancelButton = document.getElementById('cancelNPCFormBtn');
        if (cancelButton) cancelButton.click();

    } catch (e) {
        console.error("Error during window.npcTracker.renderNPCFormModal call:", e.stack || e);
        formModalError = true;
    }

    // Test renderNPCEntryView
    console.log("\nTesting window.npcTracker.renderNPCEntryView invocation...");
    global.markedMockLog.calls = 0; 
    let entryViewError = false;
    try {
        // This function, in the *current version of the code being tested*,
        // uses escapeHtml, NOT marked.parse().
        window.npcTracker.renderNPCEntryView(mockNPCEntryData, mockCampaign, 0);
        
        if (global.markedMockLog.calls === 0) {
            console.log(`SUCCESS: marked.parse was called ${global.markedMockLog.calls} times for NPC view (as expected for this code version).`);
        } else {
            console.error(`FAILURE: Expected 0 marked.parse calls for NPC view (current code uses escapeHtml), got ${global.markedMockLog.calls}.`);
            entryViewError = true;
        }
    } catch (e) {
        console.error("Error during window.npcTracker.renderNPCEntryView call:", e.stack || e);
        entryViewError = true;
    }

    if (formModalError || entryViewError) {
        process.exitCode = 1; 
    }
    console.log("--- NPC Tracker Tests Finished ---");
}

runNPCTrackerTests();
