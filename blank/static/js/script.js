$(document).ready(function() {


// Toast Messages
if ($(".toast").length) {
  $(".toast").toast("show");
}

var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
  return new bootstrap.Tooltip(tooltipTriggerEl)
})


// Tilt
if ($(".card.tilt").length) {
  VanillaTilt.init(document.querySelectorAll(".card.tilt"),{
    max: 8,
    reverse: false,
    speed: 1000,
    glare: false,
    perspective: 2000,
    easing: "cubic-bezier(.01,.98,.52,.5)",
    "max-glare": 0.1,
    gyroscope: true,
    gyroscopeMinAngleX: -45,
    gyroscopeMaxAngleX: 45,
    gyroscopeMinAngleY: -45,
    gyroscopeMaxAngleY: 45,
  });
}


// Dashboard search: Select forms
$('#search_loading_date').change(function (event) {
  $.ajax({
    data : {
      loading_date : $(this).val()
    },
    type : 'POST',
    url : '/filter_browse_form'
  })
  .done(function (data) {
    console.log(data);

    var $el = $("#search_pickup");
    var $el2 = $("#search_drop");

    if (Object.keys(data.loading).length === 0) {
      var option = $('<option></option>').attr("value", "Pickup").text("No Loads Available");
      $el.empty().append(option);
    } else {
      var option = $('<option></option>').attr("value", "Pickup").text("Select a City");
      newOptions = data.loading;
      $el.empty().append(option);
      $.each(newOptions, function(key,value) {
        $el.append($("<option></option>").attr("value", key).text(value));
      });
    }

    if (Object.keys(data.offloading).length === 0) {
      var option = $('<option></option>').attr("value", "Drop").text("No Loads Available");
      $el2.empty().append(option);
    }
    else {
      var option = $('<option></option>').attr("value", "Drop").text("Select a City");
      newOptions = data.offloading;
      $el2.empty().append(option);
      $.each(newOptions, function(key,value) {
        $el2.append($("<option></option>").attr("value", key).text(value));
      });
    }

  });
});

$('#search_pickup').change(function (event) {
  var $el = $("#search_drop");
  if ($el.val() == "Drop") {
    $.ajax({
      data : {
        loading_date : $('#search_loading_date').val(),
        pickup : $(this).val()
      },
      type : 'POST',
      url : '/filter_browse_form'
    })
    .done(function (data) {
      console.log(data);

      if (Object.keys(data).length === 0) {
        var option = $('<option></option>').attr("value", "Drop").text("No Loads Available");
        $el.empty().append(option);
      }
      else {
        var option = $('<option></option>').attr("value", "Drop").text("Select a City");
        $el.empty().append(option);
        $.each(data, function(key,value) {
          $el.append($("<option></option>").attr("value", key).text(value));
        });
      }

    });
  }
});

$('#search_drop').change(function (event) {
  var $el = $("#search_pickup");
  if ($el.val() == "Pickup") {
    $.ajax({
      data : {
        loading_date : $('#search_loading_date').val(),
        drop : $(this).val()
      },
      type : 'POST',
      url : '/filter_browse_form'
    })
    .done(function (data) {
      console.log(data);

      if (Object.keys(data).length === 0) {
        var option = $('<option></option>').attr("value", "Pickup").text("No Loads Available");
        $el.empty().append(option);
      }
      else {
        var option = $('<option></option>').attr("value", "Pickup").text("Select a City");
        $el.empty().append(option);
        $.each(data, function(key,value) {
          $el.append($("<option></option>").attr("value", key).text(value));
        });
      }

    });
  }
});


// Users OffCanvas
if ($('#usersOffcanvas').length) {
  var userCanvas = document.getElementById('usersOffcanvas')
  userCanvas.addEventListener('show.bs.offcanvas', function (event) {
    var trigger = event.relatedTarget;
    var userId = trigger.getAttribute('data-bs-UserId');
    var userName = trigger.getAttribute('data-bs-UserName');
    var userEmail = trigger.getAttribute('data-bs-UserEmail');
    var userRole = trigger.getAttribute('data-bs-UserRole');
    var userEmployer = trigger.getAttribute('data-bs-UserEmployer');
    var userLogin = trigger.getAttribute('data-bs-UserLogin');


    $('#userName').html(userName);
    $('#userEmail').html(userEmail);
    $('#userRole').html(userRole);
    $('#userEmployer').html(userEmployer);
    $('#userLogin').html(userLogin);
    $("#userAction").attr("href", "/user/action/" + userId);
  });
}



// Loads Modal
if ($('#loadsModal').length) {
  var loadCanvas = document.getElementById('loadsModal')
  loadCanvas.addEventListener('show.bs.modal', function (event) {

    var trigger = event.relatedTarget;

    var loadId = trigger.getAttribute('data-bs-LoadId');
    var loadPick = trigger.getAttribute('data-bs-LoadPick');
    var loadPickDate = trigger.getAttribute('data-bs-LoadPickDate');
    var loadDrop = trigger.getAttribute('data-bs-LoadDrop');
    var loadDropDate = trigger.getAttribute('data-bs-LoadDropDate');

    if (('#loadCancel').length) {
      $("#loadCancel").attr("href", "/loads/cancel_booking/" + loadId);
    }

    $('#loadPick').html(loadPick);
    $('#loadPickDate').html(loadPickDate);
    $('#loadDrop').html(loadDrop);
    $('#loadDropDate').html(loadDropDate);

    if ($('#formAssign').length) {

      var assignDriver = trigger.getAttribute('data-bs-LoadDriver');
      var assignCell = trigger.getAttribute('data-bs-LoadDriverCell');
      var assignID = trigger.getAttribute('data-bs-LoadDriverID');
      var assignReg = trigger.getAttribute('data-bs-LoadReg');
      var knackID = trigger.getAttribute('data-bs-LoadKnackId');

      var sap = trigger.getAttribute('data-bs-LoadSAP');


      if (sap == "") {
        $('#formAssign').hide();
        $('#formAssignMessage').html("You cannot generate a LOAD CON at the moment. We are waiting for loading reference numbers from the Supplier.");
      }
      else {
        $('#formAssignMessage').html("");
        $('#formAssign').show();
        $('#assignDriver').val(assignDriver);
        $('#assignCell').val(assignCell);
        $('#assignID').val(assignID);
        $('#assignReg').val(assignReg);
        $('#loadId').val(knackID);
      }

      $('#updateloadId').val(knackID);

      var loadRate = trigger.getAttribute('data-bs-LoadRate');
      if (loadRate){
        $("#loadBook").attr("href", "/loads/book/" + loadId + "/" + parseFloat(loadRate).toFixed(2));
      } else {
        $("#loadBook").attr("href", "/loads/book/" + loadId + "/" + "0.00");
      }

    }
    else {
      var loadRate = trigger.getAttribute('data-bs-LoadRate');
      if (loadRate){
        $("#loadBook").attr("href", "/loads/book/" + loadId + "/" + parseFloat(loadRate).toFixed(2));
      } else {
        $("#loadBook").attr("href", "/loads/book/" + loadId + "/" + "0.00");
      }
    }

  });
}




if (document.getElementById('myChart')) {
  var ctx = document.getElementById('myChart').getContext('2d');
  var myChart = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul'],
      datasets: [{
        label: 'Completed loads',
        data: [472, 424, 567, 612, 525, 525, 321],
        backgroundColor: [
          'rgba(54, 162, 235, 0.6)',
          'rgba(255, 99, 132, 0.6)',
          'rgba(255, 206, 86, 0.6)',
          'rgba(75, 192, 192, 0.6)',
          'rgba(153, 102, 255, 0.6)',
          'rgba(255, 76, 32, 0.6)',
          'rgba(255, 99, 132, 0.6)'
        ],
        borderColor: [
          'rgba(54, 162, 235, 1)',
          'rgba(255, 99, 132, 1)',
          'rgba(255, 206, 86, 1)',
          'rgba(75, 192, 192, 1)',
          'rgba(153, 102, 255, 1)',
          'rgba(255, 76, 32, 1)',
          'rgba(255, 99, 132, 1)'
        ],
        borderWidth: 1,
        barPercentage: 0.6,
      }]
    },
    options: {
      responsive: true,
      plugins: {
        legend: {
          position: 'bottom',
        },
        title: {
          display: false,
        }
      },
      scales: {
        y: {
          beginAtZero: true
        }
      }
    }
  });
}


});
