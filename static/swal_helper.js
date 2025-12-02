// Inject custom SweetAlert2 CSS
const style = document.createElement("style");
style.innerHTML = `
    /* Make the alert box bigger */
    .swal2-popup.custom-big-swal {
        width: 60rem !important;
        max-width: 90% !important;
        padding: 2rem !important;
    }

    /* Make title bigger */
    .swal2-title.big-text {
        font-size: 2rem !important;
    }

    /* Make message text bigger */
    .swal2-html-container.big-text {
        font-size: 3.5rem !important;
    }
     /* Bigger OK button */
    .swal2-confirm.big-btn {
    font-size: 2.3rem !important;
    padding: 1rem 2rem !important;
    border-radius: 0.5rem !important;
    }
    .custom-toast-size {
        font-size: 18px !important;
        padding: 20px 24px !important;
        min-height: 70px !important;
    }
`;
document.head.appendChild(style);

// Final combined SweetAlert helper
function showSwalMessage(message, duration = null) {
    Swal.fire({
        title: "Message",
        text: message,
        icon: "info",
        confirmButtonText: "OK",
        allowOutsideClick: false,
        allowEscapeKey: false,
        customClass: {
            popup: 'custom-big-swal',     // bigger box
            title: 'big-text',            // bigger title font
            htmlContainer: 'big-text',    // bigger message font
            confirmButton: 'big-btn'      // bigger OK button
        }
    }).then(() => {
        if (duration) {
            setTimeout(() => Swal.close(), duration);
        }
    });
}

function showToast(message, type = "success", duration = 5000, position = "center") {
    Swal.fire({
        toast: true,
        position: position,
        icon: type,          // "success", "error", "warning", "info", "question"
        title: message,
        showConfirmButton: false,
        timer: duration,
        timerProgressBar: true,
        customClass: {
          popup: "custom-toast-size"
        }
    });
}