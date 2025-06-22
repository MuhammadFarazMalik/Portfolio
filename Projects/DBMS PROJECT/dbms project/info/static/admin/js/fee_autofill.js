document.addEventListener('DOMContentLoaded', function () {
    console.log("fee_autofill.js loaded");

    const studentField = document.querySelector('#id_student');
    const semesterField = document.querySelector('#id_semester');

    if (studentField && semesterField) {
        console.log("Student and Semester fields found");

        studentField.addEventListener('change', function () {
            const studentId = this.value;
            console.log(`Student selected: ${studentId}`);

            if (studentId) {
                // Update the fetch URL to match the new pattern
                fetch(`/get_student_semester/${studentId}/`)
                    .then(response => {
                        if (!response.ok) {
                            throw new Error('Network response was not ok');
                        }
                        return response.json();
                    })
                    .then(data => {
                        console.log("Semester data received:", data);
                        if (data.semester !== null && data.semester !== undefined) {
                            semesterField.value = data.semester;
                        } else {
                            semesterField.value = '';
                        }
                    })
                    .catch(error => {
                        console.error('Error fetching semester:', error);
                        semesterField.value = '';
                    });
            } else {
                semesterField.value = '';
            }
        });
    }
});
