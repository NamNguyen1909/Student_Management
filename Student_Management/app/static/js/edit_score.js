document.addEventListener("DOMContentLoaded", function () {
    const subjectDropdown = document.getElementById("select-subject");
    const classDropdown = document.getElementById("select-class");
    const semesterDropdown = document.getElementById("select-semester");
    const loadScoresButton = document.getElementById("load-scores");
    const studentsTable = document.getElementById("students-table");
    const detailsDisplay = document.getElementById("details-display");
    const saveScoresButton = document.getElementById("save-scores");

    // Fetch subjects for current teacher
    fetch('/api/get-subjects')
        .then(response => response.json())
        .then(data => {
            data.forEach(subject => {
                const option = document.createElement("option");
                option.value = subject.id;
                option.textContent = subject.name;
                subjectDropdown.appendChild(option);
            });
        });

    // Enable class dropdown on subject select
    subjectDropdown.addEventListener("change", function () {
        const subjectId = this.value;
        classDropdown.disabled = false;
        classDropdown.innerHTML = '<option value="" disabled selected>-- Chọn lớp --</option>';
        semesterDropdown.disabled = true;
        semesterDropdown.innerHTML = '<option value="" disabled selected>-- Chọn học kỳ --</option>';

        fetch(`/api/get-classes/${subjectId}`)
            .then(response => response.json())
            .then(data => {
                data.forEach(cls => {
                    const option = document.createElement("option");
                    option.value = cls.id;
                    option.textContent = cls.name;
                    classDropdown.appendChild(option);
                });
            });
    });

    // Enable semester dropdown on class select
    classDropdown.addEventListener("change", function () {
        const classId = this.value;
        semesterDropdown.disabled = false;
        semesterDropdown.innerHTML = '<option value="" disabled selected>-- Chọn học kỳ --</option>';

        fetch(`/api/get-semesters/${classId}`)
            .then(response => response.json())
            .then(data => {
                data.forEach(semester => {
                    const option = document.createElement("option");
                    option.value = semester.id;
                    option.textContent = semester.name;
                    semesterDropdown.appendChild(option);
                });
            });
    });

    // Enable load scores button on semester select
    semesterDropdown.addEventListener("change", function () {
        loadScoresButton.disabled = false;
    });

    // Load students and scores
    loadScoresButton.addEventListener("click", function () {
        const subjectId = subjectDropdown.value;
        const classId = classDropdown.value;
        const semesterId = semesterDropdown.value;

        const subjectName = subjectDropdown.options[subjectDropdown.selectedIndex].text;
        const className = classDropdown.options[classDropdown.selectedIndex].text;
        const semesterName = semesterDropdown.options[semesterDropdown.selectedIndex].text;

        document.getElementById("selected-class").textContent = className;
        document.getElementById("selected-subject").textContent = subjectName;
        document.getElementById("selected-semester").textContent = semesterName;

        detailsDisplay.style.display = "block";

        fetch(`/api/get-students?class_id=${classId}&subject_id=${subjectId}`)
            .then(response => response.json())
            .then(students => {
                if (!students || students.length === 0) {
                    alert("Không có học sinh nào trong lớp này.");
                    return;
                }

                const tbody = studentsTable.querySelector("tbody");
                tbody.innerHTML = ""; // Clear old data

                students.forEach((student, index) => {
                    fetch(`/api/check-or-create-result`, {
                        method: "POST",
                        headers: {
                            "Content-Type": "application/json",
                        },
                        body: JSON.stringify({
                            student_id: student.id,
                            subject_id: subjectId,
                            semester_id: semesterId,
                        }),
                    })
                        .then(response => response.json())
                        .then(result => {
                            const row = document.createElement("tr");
                            row.setAttribute("data-student-id", student.id);
                            row.setAttribute("data-subject-id", subjectId);
                            row.setAttribute("data-semester-id", semesterId);

                            row.innerHTML = `
                                <td>${index + 1}</td>
                                <td data-student-id="${student.id}">${student.name}</td>
                                <td><input type="number" class="form-control" min="0" max="10" step="0.1" data-result-id="${result.id}" data-score-type-id="1" value="${result.score_details[0]?.value || 0}"></td>
                                <td><input type="number" class="form-control" min="0" max="10" step="0.1" data-result-id="${result.id}" data-score-type-id="2" value="${result.score_details[1]?.value || 0}"></td>
                                <td><input type="number" class="form-control" min="0" max="10" step="0.1" data-result-id="${result.id}" data-score-type-id="3" value="${result.score_details[2]?.value || 0}"></td>
                            `;
                            tbody.appendChild(row);
                        })
                        .catch(error => {
                            console.error("Error checking/creating result:", error);
                        });
                });

                studentsTable.style.display = "table";
                saveScoresButton.style.display = "block";
            })
            .catch(error => {
                console.error("Error fetching students:", error);
            });


    });
    document.getElementById("select-semester").addEventListener("change", function () {
    const semesterId = this.value;
    const subjectId = document.getElementById("select-subject").value;

    if (semesterId && subjectId) {
        fetch(`/api/get-semester-year?semester_id=${semesterId}&subject_id=${subjectId}`)
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    console.error(data.error);
                    document.getElementById("selected-year").textContent = "Không xác định";
                } else {
                    document.getElementById("selected-year").textContent = data.year;
                }
            })
            .catch(error => console.error("Error fetching semester year:", error));
    }
});
//    ==========================================================================================
//    Hàm thông báo
    function showFlashMessage(message, isError = false) {
        // Tìm container của thông báo
        const flashContainer = document.getElementById("flash-container");
        if (!flashContainer) {
            console.error("Flash container not found!");
            return;
        }

        // Tạo thẻ thông báo
        const alertDiv = document.createElement("div");
        alertDiv.className = `alert alert-dismissible fade show ${isError ? "alert-danger" : "alert-success"}`;
        alertDiv.role = "alert";
        alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        `;

        // Thêm thông báo vào container
        flashContainer.appendChild(alertDiv);

        // Tự động ẩn thông báo sau 3 giây
        setTimeout(() => {
            alertDiv.classList.remove("show"); // Bắt đầu hiệu ứng mờ dần
            setTimeout(() => alertDiv.remove(), 300); // Xóa khỏi DOM sau khi hiệu ứng hoàn tất (phù hợp với thời gian Bootstrap)
        }, 3000);
    }
    // Save scores
    saveScoresButton.addEventListener("click", function () {
        const rows = document.querySelectorAll("#students-table tbody tr");
        const scoresData = [];

        rows.forEach(row => {
            const studentId = row.getAttribute("data-student-id");
            const subjectId = row.getAttribute("data-subject-id");
            const semesterId = row.getAttribute("data-semester-id");

            if (!studentId || !subjectId || !semesterId) {
                console.error("Missing dataset attributes in row:", row);
                return;
            }

            const scores = Array.from(row.querySelectorAll("input[data-score-type-id]"))
                .map(input => ({
                    score_type_id: parseInt(input.getAttribute("data-score-type-id")),
                    value: parseFloat(input.value) || 0,
                }));

            if (scores.length > 0) {
                scoresData.push({
                    student_id: parseInt(studentId),
                    subject_id: parseInt(subjectId),
                    semester_id: parseInt(semesterId),
                    scores,
                });
            }
        });

        if (scoresData.length === 0) {
            alert("Không có dữ liệu hợp lệ để lưu.");
            return;
        }

        fetch('/api/save-scores', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(scoresData),
        })
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    showFlashMessage(`Lỗi: ${data.error}`, true);
                } else {
                    showFlashMessage("Đã lưu điểm thành công!");
                }
            })
            .catch(() => {
                showFlashMessage("Đã xảy ra lỗi kết nối.", true);
            });
    });

    let fifteenMinCount = 1;
    let fortyFiveMinCount = 1;

    // Add 15-min score column
    document.getElementById("add-15min-score").addEventListener("click", function () {
        const headerRow = document.querySelector("#students-table thead tr");
        const bodyRows = document.querySelectorAll("#students-table tbody tr");

        if (!headerRow || bodyRows.length === 0) {
            alert("Vui lòng hiển thị bảng điểm trước khi thêm cột.");
            return;
        }

        fifteenMinCount++;
        const newHeader = document.createElement("th");
        newHeader.textContent = `Điểm 15 phút ${fifteenMinCount}`;
        newHeader.setAttribute("data-type", "score-15min");
        newHeader.setAttribute("data-id", `15-${fifteenMinCount}`);
        headerRow.insertBefore(newHeader, headerRow.lastElementChild);

        bodyRows.forEach(row => {
            const newCell = document.createElement("td");
            newCell.innerHTML = `<input type="number" class="form-control" min="0" max="10" data-type="score-15min" data-id="15-${fifteenMinCount}" value="0">`;
            row.insertBefore(newCell, row.lastElementChild);
        });
    });

    // Remove 15-min score column
    document.getElementById("remove-15min-score").addEventListener("click", function () {
        if (fifteenMinCount > 1) {
            const headerRow = document.querySelector("#students-table thead tr");
            const bodyRows = document.querySelectorAll("#students-table tbody tr");

            const headerToRemove = headerRow.querySelector(`th[data-id="15-${fifteenMinCount}"]`);
            if (headerToRemove) headerRow.removeChild(headerToRemove);

            bodyRows.forEach(row => {
                const cellToRemove = row.querySelector(`td input[data-id="15-${fifteenMinCount}"]`);
                if (cellToRemove) row.removeChild(cellToRemove.parentNode);
            });

            fifteenMinCount--;
        } else {
            alert("Không thể xóa thêm cột điểm 15 phút.");
        }
    });


    // Thêm cột điểm 45 phút
    document.getElementById("add-45min-score").addEventListener("click", function () {
        fortyFiveMinCount++;
        const headerRow = document.querySelector("#students-table thead tr");
        const bodyRows = document.querySelectorAll("#students-table tbody tr");

        // Thêm header mới
        const newHeader = document.createElement("th");
        newHeader.textContent = `Điểm 45 phút ${fortyFiveMinCount}`;
        newHeader.setAttribute("data-type", "score-45min");
        newHeader.setAttribute("data-id", `45-${fortyFiveMinCount}`);
        headerRow.insertBefore(newHeader, headerRow.lastElementChild);

        // Thêm ô input cho từng học sinh
        bodyRows.forEach(row => {
            const newCell = document.createElement("td");
            newCell.innerHTML = `<input type="number" class="form-control" min="0" max="10" data-type="score-45min" data-id="45-${fortyFiveMinCount}" value="0">`;
            row.insertBefore(newCell, row.lastElementChild);
        });
    });

    // Xóa cột điểm 45 phút
    document.getElementById("remove-45min-score").addEventListener("click", function () {
        if (fortyFiveMinCount > 1) {
            const headerRow = document.querySelector("#students-table thead tr");
            const bodyRows = document.querySelectorAll("#students-table tbody tr");

            // Xóa header cuối cùng
            const headerToRemove = headerRow.querySelector(`th[data-id="45-${fortyFiveMinCount}"]`);
            headerRow.removeChild(headerToRemove);

            // Xóa ô input tương ứng
            bodyRows.forEach(row => {
                const cellToRemove = row.querySelector(`td input[data-id="45-${fortyFiveMinCount}"]`).parentNode;
                row.removeChild(cellToRemove);
            });

            fortyFiveMinCount--;
        } else {
            alert("Không thể xóa thêm cột điểm 45 phút.");
        }
    });
    });

    document.getElementById("add-15min-score").addEventListener("click", function () {
    const headerRow = document.querySelector("#students-table thead tr");
    const bodyRows = document.querySelectorAll("#students-table tbody tr");

    if (!headerRow || bodyRows.length === 0) {
        alert("Vui lòng hiển thị bảng điểm trước khi thêm cột.");
        return;
    }

    fifteenMinCount++;
    // Thêm header mới
    const newHeader = document.createElement("th");
    newHeader.textContent = `Điểm 15 phút ${fifteenMinCount}`;
    newHeader.setAttribute("data-type", "score-15min");
    newHeader.setAttribute("data-id", `15-${fifteenMinCount}`);
    headerRow.insertBefore(newHeader, headerRow.lastElementChild);

    // Thêm ô input cho từng học sinh
    bodyRows.forEach(row => {
        const newCell = document.createElement("td");
        newCell.innerHTML = `<input type="number" class="form-control" min="0" max="10" data-type="score-15min" data-id="15-${fifteenMinCount}" value="0">`;
        row.insertBefore(newCell, row.lastElementChild);
    });
    });

