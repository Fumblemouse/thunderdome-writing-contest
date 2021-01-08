flatpickr('#id_start_date', {enableTime:true, defaultDate: 'today', minDate: 'today'});
flatpickr('#id_expiry_date', {enableTime:true, defaultDate: new Date().fp_incr(7), minDate: 'today'});