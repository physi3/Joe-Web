import { initToolSelector } from '../components/tool-selector.js';
import { initPosterActions } from '../components/poster-actions.js';
import { initModal } from '../components/modal.js';
import { initSearch } from '../components/search.js';

document.addEventListener('DOMContentLoaded', () => {
    initToolSelector();
    initPosterActions();
    initModal();
    initSearch();
});
