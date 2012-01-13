<!-- HEADER ------------------------------------------------------------------>
%include header user=user, REALM=REALM

<!---------------------------------------------------------------- 
	PAGE SCRIPTS
------------------------------------------------------------------>
<script type="text/javascript">
	/**
	 * Function that redirects the user to the server's openid login
	 */ 
	function login( provider ) {
		window.open( "login?provider=" + provider + "&{{params}}", "_self" )
	}

</script>


<!---------------------------------------------------------------- 
	HEADER SECTION
------------------------------------------------------------------>

<div class="sub_header">
	<div class="page-name">LOGIN</div>
</div>


<!---------------------------------------------------------------- 
	CONTENT SECTION
------------------------------------------------------------------>
<div class="main">

	<div style="margin:25px auto; padding:15px; border:1px dotted #cccccc; width:230px;">
		<div> 
			<img src="./static/dwlogofull.png" width="220px"/>
		</div>
		<div style="text-align:left; font-style:italic; font-family:georgia; font-size:13px; color: #888888; margin:10px 0px 18px 7px;">
			Please login with one of the following providers:
		</div>
		<div id="loggedOutBox" style="margin-top:5px;" >
			<a id="google" class="openid_out" href="javascript:login('google')">	
				<img 
					onmouseover="google.className='openid_over'"
					onmouseout="google.className='openid_out'"
					src="./static/google_openid.png" 
				/></a>
			<a id="yahoo" class="openid_out" href="javascript:login('yahoo')">	
				<img 
					onmouseover="yahoo.className='openid_over'"
					onmouseout="yahoo.className='openid_out'"
					src="./static/yahoo_openid.png" 
				/></a>
			<a id="aol" class="openid_out" href="javascript:login('aol')">	
				<img 
					onmouseover="aol.className='openid_over'"
					onmouseout="aol.className='openid_out'"
					src="./static/aol_openid.png" 
				/></a>
			<a id="myopenid" class="openid_out" href="javascript:login('myopenid')">	
				<img 
					onmouseover="myopenid.className='openid_over'"
					onmouseout="myopenid.className='openid_out'"
					src="./static/myopenid_openid.png" 
				 /></a>
		</div>
	</div>
	

	
</div>

<!-- FOOTER ------------------------------------------------------------------>
%include footer