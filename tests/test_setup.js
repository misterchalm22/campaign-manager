const { JSDOM } = require('jsdom');
const fs = require('fs');
const path = require('path');

global.simpleMDEMockInstances = []; // Store all created mock instances

const SimpleMDEMock = class {
    constructor(options) {
        this.options = options;
        global.simpleMDEMockInstances.push(this); // Record instance creation

        if (options.element) {
            options.element.value = options.element.initialValue || options.element.textContent || '';
            options.element.simpleMDEMockInstance = this; // Attach mock to the element object
            // console.log(`SimpleMDE Mock constructor called for element: ${options.element.name || options.element.id}`);
        } else {
            // console.error(`SimpleMDE Mock Error: Element not provided in options: ${JSON.stringify(options)}`);
        }
    }
    value(content) {
        if (!this.options.element) return '';
        if (content !== undefined) {
            this.options.element.value = content;
        }
        return this.options.element.value;
    }
    toTextArea() {
        if (this.options.element) {
            // console.log(`SimpleMDE Mock: toTextArea called for ${this.options.element.name || this.options.element.id}`);
            delete this.options.element.simpleMDEMockInstance;
        }
    }
};

global.markedMockLog = { calls: 0, lastInput: null };
const markedMock = {
    parse: function(markdownString) {
        global.markedMockLog.calls++;
        global.markedMockLog.lastInput = markdownString;
        // console.log(`marked.parse Mock called`);
        const escapeHtml = (unsafe) => unsafe ? unsafe.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;").replace(/'/g, "&#039;") : "";
        return `<div class="mocked-markdown-output">${escapeHtml(markdownString || '')}</div>`;
    }
};

async function setupDOM() {
    const htmlPath = path.resolve(__dirname, '../index.html'); 
    const htmlContent = fs.readFileSync(htmlPath, 'utf-8');

    const dom = new JSDOM(htmlContent, {
        runScripts: "outside-only",
        url: "http://localhost/", 
        pretendToBeVisual: true,
        contentType: "text/html",
        storageQuota: 10000000 
    });

    const window = dom.window;
    global.window = window;
    global.document = window.document;
    global.navigator = window.navigator;
    global.HTMLElement = window.HTMLElement;
    global.HTMLTextAreaElement = window.HTMLTextAreaElement;
    global.HTMLInputElement = window.HTMLInputElement;
    global.HTMLButtonElement = window.HTMLButtonElement;
    global.HTMLFormElement = window.HTMLFormElement;
    global.Event = window.Event;
    global.CustomEvent = window.CustomEvent;
    global.alert = (message) => console.log(`Alert: ${message}`); // console.error for alerts might be too noisy
    global.confirm = (message) => { /* console.log(`Confirm: ${message}`); */ return true; };

    window.SimpleMDE = SimpleMDEMock;
    window.marked = markedMock;
    
    if (!window.bootstrap) {
        window.bootstrap = {
            Modal: class {
                constructor(element) { 
                    this.element = element; 
                    this.bodyElement = this.element.querySelector('#genericModalBody'); // Corrected selector
                    // console.log("Mock Bootstrap Modal constructor for", this.element.id); 
                }
                show() { 
                    // console.log("Mock Bootstrap Modal show() for", this.element.id); 
                    this.element.style.display = 'block'; 
                    // Crucially, modalUtils.showModal itself sets the innerHTML of genericModalBody
                    // So, this mock's show() doesn't need to do it.
                    // The actual genericModalBody element is part of the main document.
                }
                hide() { 
                    // console.log("Mock Bootstrap Modal hide() for", this.element.id); 
                    this.element.style.display = 'none';
                }
                static getInstance(element) { 
                    if (!element.bootstrapModalInstance) {
                        element.bootstrapModalInstance = new window.bootstrap.Modal(element);
                    }
                    return element.bootstrapModalInstance;
                }
            }
        };
        // console.log("Mocked Bootstrap Modal utility.");
    }
    
    // Ensure the modal structure from index.html is properly processed by JSDOM
    // and is available for scripts.
    const genericModalElement = window.document.getElementById('genericModal');
    if (!genericModalElement) {
        console.error("FATAL: genericModal structure not found in JSDOM document after loading index.html!");
    } else {
        // console.log("genericModal found in JSDOM document.");
        if (!window.document.getElementById('genericModalBody')) {
            console.error("FATAL: genericModalBody not found within genericModal!");
        }
    }

    const scriptsToLoad = [
        '../js/modalUtils.js', 
        '../js/dataManager.js', 
        '../js/ui.js',
        '../js/main.js', 
        // Trackers
        '../js/trackers/campaignJournal/campaignJournal.js',
        '../js/trackers/npcTracker/npcTracker.js',
        // Other trackers can be omitted if not directly under test and to speed up loading
    ];

    for (const scriptPath of scriptsToLoad) {
        const absoluteScriptPath = path.resolve(__dirname, scriptPath);
        try {
            const scriptContent = fs.readFileSync(absoluteScriptPath, 'utf-8');
            window.eval(scriptContent); 
            // console.log(`Loaded: ${scriptPath}`);
        } catch (error) {
            console.error(`Error loading script ${scriptPath}: ${error.message}\n${error.stack}`);
        }
    }
    
    try {
        window.document.dispatchEvent(new window.Event('DOMContentLoaded', {
          bubbles: true,
          cancelable: true
        }));
        // console.log("DOMContentLoaded event dispatched.");
    } catch (e) {
        console.error("Error dispatching DOMContentLoaded:", e);
    }
    
    // console.log("DOM setup complete.");
    return { window, document, dom };
}

module.exports = { setupDOM };
