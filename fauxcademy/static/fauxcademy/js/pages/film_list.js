import { initToolSelector } from '../components/tool-selector.js';
import { initPosterActions } from '../components/poster-actions.js';
import { initFilmSearch } from '../components/film-search.js';

document.addEventListener('DOMContentLoaded', () => {
    initToolSelector();
    initPosterActions();
    initFilmSearch();
});
