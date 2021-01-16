
let nowIsTheHour = new Date();

function addDays(date, days) {
    var result = new Date(date);
    result.setDate(result.getDate() + days);
    return result;
  }

flatpickr('#id_start_date', {enableTime:true, 
    defaultDate: nowIsTheHour, 
    minDate: nowIsTheHour
    });
flatpickr('#id_expiry_date', {enableTime:true, 
    defaultDate: addDays(nowIsTheHour, 7), 
    minDate: nowIsTheHour
    });
