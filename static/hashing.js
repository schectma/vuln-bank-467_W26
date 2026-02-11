
const hashModes = [
    { label: "None",   color: "#b30000" }, // Plaintext
    { label: "Weak",   color: "#ff8c00" }, // Weak
    { label: "Medium", color: "#e6b800" }, // Medium
    { label: "Strong", color: "#1f8b1f" }  // Strong
];

let hashMode = (typeof hashingData !== 'undefined') ? hashingData : 0;
//For testing colors
function updateHashingUI() {
    const btn = document.getElementById("hashingToggle");
    const mode = hashModes[hashMode] || hashModes[0];

    btn.textContent = `Toggle Hashing: ${mode.label}`;
    btn.style.backgroundColor = mode.color;
    }

async function toggleHashing(e) {
    e.preventDefault();

    try {
        const res = await fetch('/api/toggle/hashing', {
        method: 'POST'});
        const data = await res.json();
        if (data.status === 'success') {
            hashMode = data.hashmode;
            updateHashingUI();
        } else {
            alert(data.message || 'Toggle failed');
        }
    } catch (err) {
        console.error(err);
        alert('Error toggling hashing');
    }
}
document.addEventListener("DOMContentLoaded", updateHashingUI);
