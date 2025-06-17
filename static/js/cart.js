document.addEventListener('DOMContentLoaded', function() {
    const quantityInputs = document.querySelectorAll('.quantity-input');
    
    quantityInputs.forEach(input => {
        input.addEventListener('change', function() {
            const max = parseInt(this.getAttribute('max'));
            const value = parseInt(this.value);
            
            if (value > max) {
                this.value = max;
                alert(`Sorry, only ${max} items available.`);
            } else if (value < 1) {
                this.value = 1;
            }
            
            this.closest('form').submit();
        });
    });
});