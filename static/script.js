document.addEventListener('DOMContentLoaded', () => {
   const directoryInput = document.getElementById('directory-path');
   const loadBtn = document.getElementById('load-btn');
   const selectFolderBtn = document.getElementById('select-folder-btn');
   const addRuleBtn = document.getElementById('add-rule-btn');
   const rulesList = document.getElementById('rules-list');
   const previewTableBody = document.querySelector('#preview-table tbody');
   const renameBtn = document.getElementById('rename-btn');
   const statsSpan = document.getElementById('stats');
   const ruleTemplate = document.getElementById('rule-template');

   let currentFiles = [];
   let rules = [];

   // Select Folder
   selectFolderBtn.addEventListener('click', async () => {
      try {
         const response = await fetch('/api/select-folder', { method: 'POST' });
         const data = await response.json();
         if (data.path) {
            directoryInput.value = data.path;
            // Optional: Trigger load automatically
            // loadBtn.click();
         }
      } catch (e) {
         console.error(e);
         alert('Failed to open folder dialog');
      }
   });

   // Load Files
   loadBtn.addEventListener('click', async () => {
      const directory = directoryInput.value.trim();
      if (!directory) return;

      try {
         const response = await fetch('/api/files', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ directory })
         });
         const data = await response.json();

         if (data.error) {
            alert(data.error);
            return;
         }

         currentFiles = data.files;
         updatePreview();
      } catch (e) {
         console.error(e);
         alert('Failed to load files');
      }
   });

   // Add Rule
   addRuleBtn.addEventListener('click', () => {
      addRuleUI();
      updateRulesAndPreview();
   });

   // Modal Elements
   const modal = document.getElementById('confirmation-modal');
   const cancelRenameBtn = document.getElementById('cancel-rename-btn');
   const confirmRenameBtn = document.getElementById('confirm-rename-btn');

   // Rename Click - Show Modal
   renameBtn.addEventListener('click', () => {
      modal.classList.remove('hidden');
   });

   // Cancel Modal
   cancelRenameBtn.addEventListener('click', () => {
      modal.classList.add('hidden');
   });

   // Confirm Rename
   confirmRenameBtn.addEventListener('click', async () => {
      modal.classList.add('hidden');

      const directory = directoryInput.value.trim();
      const currentRules = getRulesFromUI();

      try {
         const response = await fetch('/api/rename', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ directory, rules: currentRules })
         });
         const data = await response.json();

         if (data.success) {
            alert(`Successfully renamed ${data.renamed} files.`);
            // Reload files
            loadBtn.click();
         } else {
            alert('Error: ' + (data.error || data.errors.join('\n')));
         }
      } catch (e) {
         console.error(e);
         alert('Failed to rename files');
      }
   });

   function addRuleUI() {
      const clone = ruleTemplate.content.cloneNode(true);
      const card = clone.querySelector('.rule-card');
      const select = card.querySelector('.rule-type-select');
      const body = card.querySelector('.rule-body');
      const removeBtn = card.querySelector('.remove-rule-btn');

      // Remove empty state if present
      const emptyState = rulesList.querySelector('.empty-state');
      if (emptyState) emptyState.remove();

      // Initial render of body
      renderRuleBody(body, select.value);

      // Event Listeners
      select.addEventListener('change', () => {
         renderRuleBody(body, select.value);
         updateRulesAndPreview();
      });

      removeBtn.addEventListener('click', () => {
         card.remove();
         if (rulesList.children.length === 0) {
            rulesList.innerHTML = '<div class="empty-state">No rules added yet.</div>';
         }
         updateRulesAndPreview();
      });

      // Listen for input changes in the body
      body.addEventListener('input', () => {
         updateRulesAndPreview();
      });

      rulesList.appendChild(card);
   }

   function renderRuleBody(container, type) {
      container.innerHTML = '';

      if (type === 'replace') {
         container.innerHTML = `
                <input type="text" data-key="old" placeholder="Text to replace">
                <input type="text" data-key="new" placeholder="Replacement text">
            `;
      } else if (type === 'new_name') {
         container.innerHTML = `
                <input type="text" data-key="name" placeholder="New base name">
            `;
      } else if (type === 'prepend') {
         container.innerHTML = `
                <input type="text" data-key="text" placeholder="Text to prepend">
            `;
      } else if (type === 'append') {
         container.innerHTML = `
                <input type="text" data-key="text" placeholder="Text to append">
            `;
      } else if (type === 'counter') {
         container.innerHTML = `
                <div style="display: flex; gap: 5px;">
                    <input type="number" data-key="start" value="1" placeholder="Start">
                    <input type="number" data-key="step" value="1" placeholder="Step">
                </div>
                <div style="display: flex; gap: 5px;">
                    <input type="number" data-key="padding" value="3" placeholder="Padding">
                    <input type="text" data-key="separator" value="_" placeholder="Separator">
                </div>
                <select data-key="position">
                    <option value="end">At End</option>
                    <option value="start">At Start</option>
                </select>
            `;
      } else if (type === 'extension') {
         container.innerHTML = `
                <input type="text" data-key="ext" placeholder="New extension (e.g. .jpg)">
            `;
      }
   }

   function getRulesFromUI() {
      const ruleCards = rulesList.querySelectorAll('.rule-card');
      const rules = [];

      ruleCards.forEach(card => {
         const type = card.querySelector('.rule-type-select').value;
         const inputs = card.querySelectorAll('[data-key]');
         const rule = { type };

         inputs.forEach(input => {
            rule[input.dataset.key] = input.value;
         });

         rules.push(rule);
      });

      return rules;
   }

   function updateRulesAndPreview() {
      // Debounce could be added here
      updatePreview();
   }

   async function updatePreview() {
      if (currentFiles.length === 0) return;

      const directory = directoryInput.value.trim();
      const rules = getRulesFromUI();

      try {
         const response = await fetch('/api/preview', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ directory, rules })
         });
         const data = await response.json();

         renderPreview(data.preview);
      } catch (e) {
         console.error(e);
      }
   }

   function renderPreview(previewData) {
      previewTableBody.innerHTML = '';
      let changedCount = 0;

      previewData.forEach(item => {
         const tr = document.createElement('tr');
         const isChanged = item.changed;
         if (isChanged) changedCount++;

         tr.innerHTML = `
                <td>${item.original}</td>
                <td class="${isChanged ? 'changed' : ''}">${item.new}</td>
                <td>
                    <span class="status-icon ${isChanged ? 'status-changed' : 'status-unchanged'}"></span>
                    ${isChanged ? 'Modified' : 'Unchanged'}
                </td>
            `;
         previewTableBody.appendChild(tr);
      });

      statsSpan.textContent = `${previewData.length} files | ${changedCount} will be renamed`;
      renameBtn.disabled = changedCount === 0;
   }
});
