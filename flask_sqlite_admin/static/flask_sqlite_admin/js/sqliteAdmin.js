/* Admin Page */

// tab loading functions
var activaTab = function(tab){
    $('.nav-tabs a[href="#' + tab + '"]').tab('show');
};
var loadTab = function(){
	// hide elements
	$(".state-edit").hide()
	$(".glyphicon-wrench").hide()
	$(".add-detail").hide()
	$(".x-wrench").hide()
	
	// trigger tooltips/popovers
	$("[data-toggle='tooltip']").tooltip()
	$("[data-toggle='popover']").popover()
}

// ajax fetch tab data
var fetchTabHTML = function(tab,sort,dir,offset){
	sort = typeof sort !== 'undefined' ? sort : '';
	dir = typeof dir !== 'undefined' ? dir : 'asc';
	offset = typeof offset !== 'undefined' ? offset : '0';
	
	$.get(
		window.location+'api?table='+tab+'&sort='+sort+'&dir='+dir+'&offset='+offset,
		function(data){
			$("#"+tab).html(data)
			loadTab()
		}
	)
	.fail(function(d) {
		$("#"+tab).html('<div class="alert alert-danger margin4020" role="alert">An error occurred. Check <a href="'+window.location+'api?table='+tab+'&sort='+sort+'&dir='+dir+'&offset='+offset+'" target="_blank">here</a> for more information</div>')
		console.log(d.responseText)
	})
}

// fetch tab data for first tab on page load
$(function(){
  var tab = $(".active").find("[data-toggle=tab]").text()
  if( tab == '' ){
    console.log("  ## current tab is null")
	  tab = $("[data-toggle=tab]").first().text()
  }

	fetchTabHTML(tab)
	activaTab(tab)
	
})

// fetch tab data when tab clicked
$(document.body).on("click","[data-toggle=tab]",function(e){
	fetchTabHTML($(this).text())
})

//refresh tab data when "refresh" button clicked
$(document.body).on("click",".alert-link",function(e){
	e.preventDefault()
	tab = $(this).closest('.tab-pane').attr('id')
	fetchTabHTML(tab)
	activaTab(tab)	
})

//pagination
$(document.body).on("click",".pagination li:not([class=disabled]) a",function(e){
	e.preventDefault()
	d = $(this).data('q')
	o = $(this).data('offset')
	fetchTabHTML(d['table'],d['sort'],d['dir'],o)
})

// column sorting
$(document.body).on("click",".th-sort",function(e){
	e.preventDefault()
	d = $(this).data('q')
	c = $(this).text()
	// flips
	dir = 'asc'
	if (d['sort'] == c && d['dir'] == 'asc'){
		dir = 'desc'
	}
	fetchTabHTML(d['table'],c,dir,d['offset'])
})


/* Admin Ajax Page */

$(document.body).on("change", "#field_type", function(){

	$.ajax({
		url: window.location+'selected', 
		type: 'POST',
		dataType: "json",
		data: {
			'selected': $(this).val()
		},
    success: function(data) {
			if (data.status==1){
				returnHTML(1,data.message)
				close_edit(_that)
				staticUpdate()
			} else {
				returnHTML(0,data.error)
			}
		}//end success
	})//end ajax

})

// mouseovers for edit symbol

$(document.body).on("mouseenter","th",function(){
	$(this).find('.glyphicon-trash').show()
})
$(document.body).on("mouseleave","th",function(){
	$(this).find('.glyphicon-trash').hide()
})
$(document.body).on("mouseenter","th",function(){
	$(this).find('.glyphicon-plus').show()
})
$(document.body).on("mouseleave","th",function(){
	$(this).find('.glyphicon-plus').hide()
})

$(document.body).on("mouseover","tr",function(){
	//$(this).find('.glyphicon-plus').show()
})
$(document.body).on("mouseout","tr",function(){
	//$(this).find('.glyphicon-plus').hide()
})

$(document.body).on("mouseover","tr",function(){
	$(this).find('.glyphicon-wrench').show()
})
$(document.body).on("mouseout","tr",function(){
	$(this).find('.glyphicon-wrench').hide()
})
$(document.body).on("mouseover",".wrench",function(){
	$(this).removeClass('text-muted')
})
$(document.body).on("mouseout",".wrench",function(){
	$(this).addClass('text-muted')
})

//click for del 
$(document.body).on("click",".glyphicon-trash",function(){
  var del_col = $(this).parent().find(".th-sort").text()
  //var tab = $("[data-toggle=tab]").first().text()
  var tab = $(".active").find('a[data-toggle="tab"]').text()
  console.log("  ## deleting column in table: ", tab)
  console.log("  ##deleting column::" , del_col)
  /*
  $.post(
    window.location+'api',
    JSON.stringify({
      command: 'del_col',
      data: 'str1',
    }),
    function(response){
      alert('col',del_col,' deleted')
    },
    "json"
  );
  */
	$.ajax({
		type: 'POST',
    contentType: "application/json",
		url: window.location+'api', 
		dataType: 'json',
		data: JSON.stringify({"command":"del_col", "data": del_col, "table":tab}),
    success: function(data) {
      alert("deleted a col, status:" + data.status);
      fetchTabHTML(tab)
      activaTab(tab)
		},
    error: function(result){
      console.log(result);
    } 

	})
  //end ajax
})

// clicks for edit wrench
$(document.body).on("click",".open-edit",function(){
	$("#tr-"+$(this).data('table')+"-"+$(this).data('id')).find(".state-edit").show()
	$("#tr-"+$(this).data('table')+"-"+$(this).data('id')).find(".state-rest").hide()
	$(this).closest(".popover").popover('hide').siblings('.wrench').hide().siblings(".x-wrench").show()
})
var close_edit = function(_that){
	elem = $("#tr-"+$(_that).data('table')+"-"+$(_that).data('id'))
	if ($(_that).data('action')=='delete'){
		elem.hide()
	} else {
		elem.find(".state-edit").hide()
		elem.find(".state-rest").show()
		elem.find(".x-wrench").hide().siblings('.wrench').show()
	}
}
$(document.body).on("click",".close-edit",function(){
	close_edit(this)
})

// clicks for add button
$(document.body).on("click",".add-btn",function(){
	$(this).hide().siblings(".add-detail").show()
})
$(document.body).on("click",".add-btn-close",function(){
	$(this).parent().parent().hide().siblings(".add-btn").show()
})

// click feedback close
$(document.body).on("click",".edit-feedback-close",function(){
	$(this).closest('tr').hide()
})

// main api
$(document.body).on("click",".edit-save",function(e){
	// pull post data out of button
	var postData = {}
	if(!$(this).data('id')){
		_trId = 0
	} else {
		_trId = $(this).data('id')
		_that = this
	}
	//postData['id']=$(this).data('id')
	//postData['primaryKey']=$(this).data('primarykey')
	//postData['action']=$(this).data('action')
	//postData['table']=$(this).data('table')
	
	// pull post data from inputs
	var _tr = $("#tr-"+ $(this).data('table') +"-"+_trId)
	_tr.find('input').each(function(){
    if (this.value != 'None'){ 
		  postData[this.name] = this.value
    }
	})
	
	// update static fields
	var staticUpdate = function(){
		_tr.find('input').each(function(){
			$(this).siblings('span').html(this.value)
		})
	}
	
	// create feedback html
	var returnHTML = function(status,content){ 
		_html = '<td colspan="'+_tr.children().length+'">'
		if (status == 1){
			_html += '<div class="alert alert-success alert-dismissible noMargin" role="alert">Success. '+content
		} else {
			_html += '<div class="alert alert-warning alert-dismissible noMargin" role="alert">Error: '+content
		}
		_html += '<button type="button" class="close edit-feedback-close"><span aria-hidden="true">&times;</span></button></div></td></tr>'
		_tr.after('<tr class="edit-feedback">'+_html+'</tr>')
	}
	
	// post request
	/*
	$.post( 
		window.location+'api', 
		postData,
		function(data){
			if (data.status==1){
				returnHTML(1,data.message)
				close_edit(_that)
				staticUpdate()
			} else {
				returnHTML(0,data.error)
			}
		},
		"json"
	)
	.fail(function(d) {
		console.log(d.responseText)
		_tr.after(returnHTML(0,'An error occurred. Refer to console for more information'))
	})
	*/

  method = $(this).data('method')
  if (method == 'save_row'){
	  console.log("##saving, postdata:", postData)
    $.ajax({
      type: 'POST',
      contentType: "application/json",
      url: window.location+'api', 
      dataType: 'json',
      data: JSON.stringify({'id':$(this).data('id'),'command':'save_row','table':$(this).data('table'),'row':postData}),
      success: function(data) {
        console.log("  ##got data:",data)
				returnHTML(1,data.message)
				close_edit(_that)
				staticUpdate()
      },
      error: function(result){
    		returnHTML(0,result.error)
				close_edit(_that)
				staticUpdate()
        console.log(result);
      } 
    });
    return;

  }else if (method == 'delete_row'){
    console.log("  ## delete a row")
    $.ajax({
      type: 'POST',
      contentType: "application/json",
      url: window.location+'api', 
      dataType: 'json',
      data: JSON.stringify({"command":"del_row", "id":$(this).data('id'), "table":$(this).data('table')}),
      success: function(data) {
				returnHTML(1,data.message)
				close_edit(_that)
				staticUpdate()
        /*
        alert("deleted a col, status:" + data.status);
        fetchTabHTML(postData['table'])
        activaTab(postData['table'])
        */
      },
      error: function(result){
        console.log(result);
    		returnHTML(0,result.error)
				close_edit(_that)
				staticUpdate()
      } 

    })

    return 
  }

  console.log("##request api here, method:",$(this).data('method'), ", postData:", postData)
	$.ajax({
		url: window.location+'api', 
		type: $(this).data('method'),
		dataType: "json",
		data: postData,
    success: function(data) {
			if (data.status==1){
				returnHTML(1,data.message)
				close_edit(_that)
				staticUpdate()
			} else {
				returnHTML(0,data.error)
			}
		}
	})
	.fail(function(d) {
		console.log("##Error :", d.responseText)
		_tr.after(returnHTML(0,'An error occurred. Refer to console for more information'))
	})
})
