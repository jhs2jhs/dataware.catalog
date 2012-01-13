<!-- HEADER ------------------------------------------------------------------>
%include header user=user, REALM=REALM

<!---------------------------------------------------------------- 
	PAGE SCRIPTS
------------------------------------------------------------------>

<!-- Include required JS files -->
<script type="text/javascript" src="static/shCore.js"></script>
<script type="text/javascript" src="static/shBrushPython.js"></script>
<script type="text/javascript" src="static/jquery-impromptu.3.2.js"></script>

<!-- Include *at least* the core style and default theme -->
<link href="static/shCore.css" rel="stylesheet" type="text/css" />
<link href="static/impromptu.css" rel="stylesheet" type="text/css" />
<link href="static/shThemeDefault.css" rel="stylesheet" type="text/css" />
 
<script>

	function resource_error_box( error ) {
		msg = "<span class='resource_error_box'>RESOURCE ERROR:</span>&nbsp;&nbsp;" + error
		$.prompt( msg,  {  buttons: { Continue: true }	} )
	}

	////////////////////////////////////////////////////
	
	function forwarding_box( error, redirect ) {
		msg = "<span class='resource_error_box'>RESOURCE SAYS:</span>&nbsp;&nbsp;<i>\"" + error + "\"</i><br/>";
		msg += "<span class='resource_error_box'>There is no choice but to reject the request.</span>";
		$.prompt( msg,  {  
			buttons: { Continue: true },
			callback: function ( v, m, f ) { 
				window.location = redirect;
			}
		} )
	}

	////////////////////////////////////////////////////

	function error_box( error ) {
		msg = "<span class='error_box'>ERROR:</span>&nbsp;&nbsp;" + error
		$.prompt( msg,  {  buttons: { Continue: true }, } )
	}

	////////////////////////////////////////////////////

	function authorize_request( request_id ) {
		$.prompt(
			'Are you sure you want to authorize this request?', 
			{ 
				buttons: { Yes: true, Cancel: false },
				callback: function ( v, m, f ) { 
					if ( v == false ) return;
					else authorize_request_ajax( request_id )
				}
			}
		)
	}

	////////////////////////////////////////////////////

	function reject_request( request_id ) {
		$.prompt(
			'Are you sure you want to reject this request?', 
			{ 
				buttons: { Yes: true, Cancel: false },
				callback: function ( v, m, f ) { 
					if ( v == false ) return;
					else reject_request_ajax( request_id )
				}
			}
		)
	}

	////////////////////////////////////////////////////

	function revoke_request( request_id ) {
		$.prompt(
			'Are you sure you want to revoke this request?', 
			{ 
				buttons: { Yes: true, Cancel: false },
				callback: function ( v, m, f ) { 
					if ( v == false ) return;
					else revoke_request_ajax( request_id )
				}
			}
		)
	}

	////////////////////////////////////////////////////

	function authorize_request_ajax( request_id ) {
		$.ajax({
			type: 'POST',
			url: "/authorize_request",
			data: "request_id=" + request_id,
			success: function( data, status  ) {
				data = eval( '(' + data + ')' );
				if ( data.success ) {
					window.location = data.redirect;
				} else if ( data.cause == "resource_provider" ) {
					forwarding_box( data.error, data.redirect );
				} else {
					error_box( data.error );
				}
			},
			error: function( data, status ) {
				error_box( "Unable to contact server at this time. Please try again later." );
			}
		});
	}

	////////////////////////////////////////////////////

	function reject_request_ajax( request_id ) {
		$.ajax({
			type: 'POST',
			url: "/reject_request",
			data: "request_id=" + request_id,
			success: function( data, status ) {
				data = eval('(' + data + ')');
				if ( data.success ) {
					window.location = data.redirect;
				} else {
					error_box( data.error );
				}
			},
			error: function( data, status ) {
				error_box( "Unable to contact server at this time. Please try again later." );
			}
		});		
	}

	////////////////////////////////////////////////////

	function revoke_request_ajax( request_id ) {
		$.ajax({
			type: 'POST',
			url: "/revoke_request",
			data: "request_id=" + request_id,
			success: function( data, status  ) {
				data = eval( '(' + data + ')' );
				if ( data.success ) {
					window.location = data.redirect;
				} else if ( data.cause == "resource_provider" ) {
	 				resource_error_box( data.error )
				} else {
					error_box( data.error )
				}
			},
			error: function( data, status ) {
				error_box( "Unable to contact server at this time. Please try again later." );
			}
		});
	}

	////////////////////////////////////////////////////

	function toggle( request_id ) {
		full = $( "#request_" + request_id + "_full" );
		preview = $( "#request_" + request_id + "_preview" );

		if ( full.css( "display" ) == "none" ) {
			full.css( "display", "block" );
			preview.css( "display", "none" );
		} else {
			full.css( "display", "none" );
			preview.css( "display", "block" );
		}
	}
</script>

<!---------------------------------------------------------------- 
	HEADER SECTION
------------------------------------------------------------------>

<div class="sub_header">
	<div class="page-name">AUDIT</div>
</div>

<style>

.error_box {
	background-color:#dd3333;
	color:#ffffff;
	padding:2px 5px 2px 5px;
}

.resource_error_box {
	background-color:#dd33dd;
	color:#ffffff;
	padding:2px 5px 2px 5px;
}

.item_number {
	float:left; 
	background-color:#aa6666; 
	font-size:15px; 
	color:#ffffff; 
	height:80px; 
	width:40px; 
	padding:5px;
}

.request_attribute {
	overflow:auto;
}

.item_name {
	margin:1px; 
	background-color:#ffeeee;
	font-size:11px; 
	color:#aa6666; 
	padding:3px;
	text-align:right;
	float:left;
	font-family:arial;
}

.item_value {
	margin:1px 4px;
	font-size:11px; 
	color:#777788; 
	padding:3px;
	text-align:right;
	float:left;
	font-family:arial;
}

.request_box {
	margin:5px 0px 20px 5px; 
	font-size:11px; 
	overflow:auto;
}

</style>
<!---------------------------------------------------------------- 
	CONTENT SECTION
------------------------------------------------------------------>
<div class="main">

	<!---------------------------------------------------------------- 
		THE DATA TABLE
	------------------------------------------------------------------>
	<div style="float:left; clear:both;">
		<div>
			%for request in requests:
			<div id='request_{{request["request_id"]}}' class="request_box">
				<div class="item_number">{{request["request_id"]}}</div>
				<div style="float:left;" >
					<div style="width:954; height:5px; background-color:#aa6666;"> </div>
					<div style="float:left; width:257px;" >
						<div class="request_attribute">
							<div class="item_name" >request from:</div>
							<div class="item_value" >{{request["client_name"]}}</div>
						</div>
						<div class="request_attribute">
							<div class="item_name" >resource name:</div>
							<div class="item_value" >{{request["resource_name"]}}</div>
						</div>
						<div class="request_attribute">
							<div class="item_name" >current status:</div>
							<div class="item_value" >{{request["request_status"]}}</div>
						</div>
						<div class="request_attribute">
							<div class="item_name" >expiry time:</div>
							<div class="item_value" >{{request["expiry_time"]}}</div>
						</div>
						<div style="margin:3px">
							%if request["request_status"] == "PENDING":
								<a href='javascript:authorize_request({{request["request_id"]}})'>authorize</a> |
								<a href='javascript:reject_request({{request["request_id"]}})'>reject</a>
							%elif request["request_status"] == "ACCEPTED":
								<a href='javascript:revoke_request({{request["request_id"]}})'>revoke</a>
							%end
						</div>
					</div>
					<div style="font-size:12px; float:left; overflow:none; width:700px;">
						<div class="item_name" style="width:690px; text-align:left; margin-bottom:10px;">
							requested processor <i>(for {{request["resource_id"]}})</i>:
					%if request[ "query" ] != request [ "preview"] :
								<a href='javascript:toggle({{request["request_id"]}})'>toggle preview</a>
						</div>
						<div id='request_{{request["request_id"]}}_preview'>
							<code class="brush: python; toolbar: false">{{request["preview"]}}</code>
							<div class="item_name" style="float:right; margin-top:-15px;">. . . end of preview</div>
						</div>
						<div id='request_{{request["request_id"]}}_full' style="display:none; margin-left:-6px;">
							<code class="brush: python; toolbar: false">{{request["query"]}}</code>
						</div>
					%else:
						</div>
						<div>
							<code class="brush: python; toolbar: false">{{request["query"]}}</code>
						</div>
					%end
					</div>
				</div>
			</div>
			%end
		</div>	
	</div>	
</div>

<!-- Finally, to actually run the highlighter, you need to include this JS on your page -->
<script type="text/javascript">
	SyntaxHighlighter.config.tagName = "code";
    SyntaxHighlighter.all()
</script>

<!-- FOOTER ------------------------------------------------------------------>
%include footer

