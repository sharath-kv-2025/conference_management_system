// Conference Management System - Main JS File
console.log('Conference Management System loaded');

// Global utilities for the conference system
window.ConferenceUtils = {
    formatDate: function(dateStr) {
        if (!dateStr) return '';
        const date = new Date(dateStr);
        return date.toLocaleDateString();
    },
    
    formatTime: function(timeStr) {
        if (!timeStr) return '';
        return timeStr;
    }
};