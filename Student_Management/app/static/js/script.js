document.addEventListener("DOMContentLoaded", function () {
    // Thông báo
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

    // Ví dụ sử dụng:
    // showFlashMessage("Đây là thông báo thành công!", false);
    // showFlashMessage("Đây là thông báo lỗi!", true);
});
