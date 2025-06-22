document.addEventListener('DOMContentLoaded', function () {
    const dobField = document.querySelector('#id_DOB');
    const classIdField = document.querySelector('#id_class_id');
    const usnField = document.querySelector('#id_USN');

    function updateUSN() {
        const dob = dobField.value;
        const classId = classIdField.options[classIdField.selectedIndex]?.text;

        if (dob && classId) {
            const year = new Date(dob).getFullYear().toString().slice(-2); // Extract last two digits of the year
            const deptName = classId.split(':')[0].trim().toLowerCase().replace(/\s+/g, '-'); // Extract department name
            usnField.value = `${year}-${deptName}`; // Auto-fill USN
        }
    }

    dobField.addEventListener('change', updateUSN);
    classIdField.addEventListener('change', updateUSN);
});
