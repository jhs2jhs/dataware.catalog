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

<!-- Include *at least* the core style and default theme -->
<link href="static/impromptu.css" rel="stylesheet" type="text/css" />
<link rel="stylesheet" type="text/css" href="./static/layout.css" /> 

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

		<div style="font-size:13px; background-color:#dd3333; width:130px; color:#ffffff; padding:2px 5px 2px 5px;">
			<b>Request Failure</b>
		</div>

		<div style="margin:5 0 30 0; color:#a66767;">
			<div style="float:left; font-size:13px; background-color:#993333; width:55px; color:#ffffff; padding:2px 5px 2px 5px;">
				cause:
			</div>
			<div style="margin-left:70px;padding:2px 5px 2px 2px;">
				{{error}}
			</div>
		</div>

		<div style="border-top:1px dotted gray; padding-top:15px">
			<i>Please contact the resource provider in order to correct these problems. For some reason the resource is not according 
			with the dataware <a href="https://github.com/jog/dataware.catalog/wiki/Dataware-v2---resource-protocol">installation protocol</a>.</i>
		</div>
	</div>
	
</div>
</body>
</html>