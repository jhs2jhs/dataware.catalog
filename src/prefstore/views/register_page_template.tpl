<!-- HEADER ------------------------------------------------------------------>
%include header user=user

<!---------------------------------------------------------------- 
	PAGE SCRIPTS
------------------------------------------------------------------>
<script type="text/javascript">
	/**
	 * Function that redirects the user to the server's openid login
	 */ 
	function login( provider ) {
		window.open( "login?provider=" + provider, "_self" )
	}

</script>


<!---------------------------------------------------------------- 
	HEADER SECTION
------------------------------------------------------------------>

<div class="sub_header">
	<div class="page-name">REGISTRATION</div>
	<div class="page-description">WE JUST NEED A COUPLE MORE DETAILS...</div>
</div>


<!---------------------------------------------------------------- 
	CONTENT SECTION
------------------------------------------------------------------>
<div class="main">

	<div style="margin:25px auto; padding:15px; border:1px dotted #cccccc; width:400px; height:240px;">
		<div> 
			<img src="./static/dwlogofull.png" width="220px"/>
		</div>
		<div style="text-align:left; font-style:italic; font-family:georgia; font-size:12px; color: #888888; margin:10px 0px 18px 7px;">
			This seems to be the first time you have logged in. To activate your account
			please pick a screen name, and register an email address:
		</div>
		<div id="loggedOutBox" >
        <form action="http://localhost:8080/register" method="GET" >
			<div style="padding:0 10 0 8; float:left; border:0px dotted; height:100px; font-size:12px; font-family:georgia; color:#555555;">
	            <div>Screen Name:
				%if "screen_name" in errors:
					<span class="loginMessage"> {{errors[ "screen_name" ]}}</span>
				%end
				</div>
		        <div>
			        <input id="jid" class="text" name="screen_name" value="{{screen_name}}" type="text" size="37" />
				</div>

	            <div style="margin-top:5px;">
					Email:
					%if "email" in errors:
						<span class="loginMessage"> {{errors[ "email" ]}}</span>
					%end
				</div>
		        <div class="right">
			        <input id="email" class="text" name="email" value="{{email}}"  type="text" size="37" />
				</div>
			</div>
				
			<input type="submit" value="Register >>" style="margin-top:60px; float:bottom; " />
			
			<input type="hidden" name="submission" value="True" />
		</form>
		</div>
	</div>	
</div>

<!-- FOOTER ------------------------------------------------------------------>
%include footer