// Call the dataTables jQuery plugin
$(document).ready(function() {


	// GENERIC
  $('#dataTable').DataTable()

	//
// CHURNING USERS
// Call the dataTables jQuery plugin
  // HIGHLIGHT FOR USERS
  const USER_COLUMN_MAPPING = {
			'#':0,
			'Username':1,
			'session_active_total':2,
			'session_skip_total':3,
			'session_skip_streak':4,
			'days_active_total':5,
			'days_since_join':6
  }
  let total_churning = 0;
  let total_users = 0;
  function is_user_churning(data){
	  return data[USER_COLUMN_MAPPING['session_active_total']] > 1 && data[USER_COLUMN_MAPPING['session_skip_streak']] >= 2;
  }
  $('#usersDataTable').DataTable({
	  "createdRow": function( row, data, dataIndex){
				total_users += 1;
			if( is_user_churning(data) ){
				$(row).addClass('bg-warning');
				total_churning += 1;
			}
		  //#ffd7d7
		}
  });
  $("#total_churning").html(total_churning);
  $("#total_users").html(total_users);
  $("#total_churning_bar").css('width',((total_churning/total_users)*100).toString()+"%")
  

});
