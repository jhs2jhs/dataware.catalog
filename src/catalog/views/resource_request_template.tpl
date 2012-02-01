<html>
<head>
<title>Permission to Install Resource...</title>
</head>
<body>

<!---------------------------------------------------------------- 
	PAGE SCRIPTS
------------------------------------------------------------------>
<!-- Include required JS files -->
<script type="text/javascript" src="./static/jquery-1.6.min.js"></script> 
<script type="text/javascript" src="static/jquery-impromptu.3.2.js"></script>

<link href="static/impromptu.css" rel="stylesheet" type="text/css" />
<link rel="stylesheet" type="text/css" href="./static/layout.css" /> 

<script type="text/javascript">
	
	function authorize_resource() {
		$.prompt(
			'Are you sure you want to install this resource?', 
			{ 
				buttons: { Yes: true, Cancel: false },
				callback: function ( v, m, f ) { 
					if ( v == false ) return;
					else authorize_resource_ajax()
				}
			}
		)
	}

	////////////////////////////////////////////////////

	function authorize_resource_ajax() {
		$.ajax({
			type: 'POST',
			url: "/resource_authorize",
			data: 'resource_id={{resource["resource_id"]}}&state={{state}}&redirect_uri={{resource["redirect_uri"]}}',
			success: function( data, status  ) {

				data = eval( '(' + data + ')' );
				if ( data.success ) {
					window.location = data.redirect;
				} else {
					error_box( data.error );
				}
			},
			error: function( data, status ) {
				error_box( "We are currently unable to process this installation. Please try again later." );
			}
		});
	}

	////////////////////////////////////////////////////

	function reject_resource( error ) {

		window.location.href =  
			'{{resource["redirect_uri"]}}' +
			'?state={{state}}' +
			'&error=access_denied' +
			'&error_description=' + error ;
	}

	////////////////////////////////////////////////////

	function error_box( error ) {
		msg = "<span class='error_box'>ERROR:</span>&nbsp;&nbsp;" + error
		$.prompt( msg,  {  buttons: { Continue: true }, } )
	}

</script>


<style>
	.error_box {
		background-color:#dd3333;
		color:#ffffff;
		padding:2px 5px 2px 5px;
	}
</style>

<!---------------------------------------------------------------- 
	CONTENT SECTION
------------------------------------------------------------------>
<div class="main">
	<div style="margin:25px auto; padding:15px; border:1px dotted #cccccc; width:420px; 
	text-align:left; font-family:georgia; font-size:13px; color: #888888; ">
		<div> 
			<img src="./static/dwlogofull.png" width="220px"/>
		</div>
		<div style="font-style:italic; margin:5 0 0 2;">
			A dataware resource is asking to be installed to your catalog:
		</div>

		<div style="border-bottom:1px dotted gray; border-top:1px dotted gray; padding:10 0 10 0; margin:14 0 20 0;
			font-family:georgia; font-size:18px; color:#864747">
			INSTALLATION REQUEST
		</div>

		<div>
			<div style="float:left; margin:0 8 0 1">
				%if resource[ "logo_uri" ]:
					%if resource[ "web_uri" ]:
						<a href='{{resource[ "web_uri" ]}}' target='_blank'><img src='{{resource[ "logo_uri" ]}}' style='width:70px; height:70px'/></a>
					%else:
						<img src='{{resource[ "logo_uri" ]}}' style='width:70px; height:70px'/>
					%end
				%else:
					%if resource[ "web_uri" ]:
						<a href='{{resource[ "web_uri" ]}}' target='_blank'><img src='./static/unknown.png' style='width:70px; height:70px'/></a>
					%else:
						<img src='./static/unknown.png' style='width:70px; height:70px'/>
					%end
				%end
			</div>
			<div style="margin-left:80px">
				<div>
					%if resource[ "web_uri" ]:
						<a style='color:9f5102' href='{{resource[ "web_uri" ]}}' target='_blank' style="font-size:14px; font-weight:bold; color:#864747;">{{resource[ "resource_name" ]}}</a>
					%else:
						<b style='color:9f5102'>{{resource[ "resource_name" ]}}</b>
					%end
				</div>
				<div style="margin-top:10"> <b>registered:</b> 
				%import time
				{{time.strftime( "%d %b %Y", time.gmtime( resource[ "registered" ] ) )}}
				</div>	
				<div style="margin-top:10"> <b>description:</b> {{resource[ "description" ]}} </div>		
					
			</div>

			<div style="margin:20 0 10 0; text-align:right;">
			%if user:
				<a href="javascript:authorize_resource()" style="font-size:14px;">install</a> |
				<a href="javascript:reject_resource('The+user+denied+your+request')" style="font-size:14px;">reject</a>
			%else:
				<a href='login?resource_id={{resource["resource_id"]}}&redirect_uri={{resource["redirect_uri"]}}&state={{state}}' style="font-size:14px;">login</a>
			%end
			<div>
		</div>
	</div>
	
</div>
</body>
</html>