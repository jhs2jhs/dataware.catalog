<!-- HEADER ------------------------------------------------------------------>
%include header user=user, REALM=REALM

<!---------------------------------------------------------------- 
	PAGE SCRIPTS
------------------------------------------------------------------>
<script type="text/javascript">
</script>


<!---------------------------------------------------------------- 
	HEADER SECTION
------------------------------------------------------------------>

<div class="sub_header">
	<div class="page-name">HOME</div>
	<div class="page-description">
		WELCOME TO THE DATAWARE CATALOG - HELPING TO MANAGING YOUR DATA LIFE
	</div>
</div>


<style>

.blurb {
	display: table-cell;
	clear: both;
	padding-left: 75px;
}

.blurb_item {
	background-color: #ffffff;
	float: left;
	width:275;
	margin:2px;
	padding:8px;
}

.instructions {
	border: 1px dotted blue;
}

.blurb_header {
	font-size:22; 
	font-weight:bold; 
	color:#994747;
	margin-bottom:4px;
}

.blurb_icon {
	float:left;
	margin-right:5px;
}

.blurb-description {
	float:left;
	color: gray;
	font-size: 13px;
	font-style: italic;
	margin-bottom: 10px;
}

.separator{
	border-top: 1px dotted gray;
	height:18px;
}

.instruction-header {
	font-size:26;
	color:#f0f0ff;
	font-weight:bold; 
	background-color: #994747;
	width:120px;
}

.instruction-description {
	color: #777777;
	font-size: 16px;
}

.extension_out {
	width:185px; 
	vertical-align:text-top
}

</style>


<!---------------------------------------------------------------- 
	CONTENT SECTION
------------------------------------------------------------------>
<div class="main">

	<div class="blurb">
		<div class="blurb_item">
			<div class="blurb_header">Your interests...</div>
			<div class="blurb-description">
				Web sites all over the web have created models of your preferences and interests.
				All partial, all incomplete... and all owned by someone else!
			</div>

			<div class="blurb-description">
				 <b>A Prefstore can change all that.</b><br/>
				 See the instructions below, on how to get started in 3 steps.
			</div>
		</div>
		<div class="blurb_item">
			<div class="blurb_header">Based on your data...</div>
			<div class="blurb-description">
				And you don't have to lift a finger.
				You just create a prefstore account, add the chrome extension and... well, that's it.
				The software creates a model for you by summarizing how you interact with the web.
			</div>	

			<div class="blurb_header">Under your control...</div>
			<div class="blurb-description">
				This is your model. 100% Private. You can update it, tweak it and even
				delete it, whenever you see fit! 
			</div>
		</div>
		<div class="blurb_item">
			<div class="blurb_header">Personalize services</div>
			<div class="blurb-description" >
				<img src="static/dwlogo.png" style="float:left; padding-right:5px; width:50px;"/>
				A prefstore is also dataware, and can be part of your datasphere.<br/>
				But what does this mean?
			</div>
			<div class="blurb-description">
				It means that, <b>if you want to</b>, you can allow 3rd party apps to filter 
				their services against it. 
			</div>
			<div class="blurb-description">				
				This allows you to maintain privacy while creating <b>personalized experiences</b>.
			</div>
		</div>
	</div>
	
	<div class="separator"></div>

	<!---------------------------------------------------------------- 
		INSTRUCTIONS SECTION
	------------------------------------------------------------------>
	<div style="float:left; margin-left:85px; width:300px; border:0px dotted gray">
		<div style="width:300px; margin-bottom:25;">
			<div class="instruction-header">
				Step 1.
			</div>
			<div class="instruction-description">
				Install the Google Chrome Plugin in your browser, by clicking on the icon below:
				<a href="static/prefstore_extension.crx">
					<img 
						class="extension_out" 
						src="static/prefstore_extension_blue.png"
						onmouseover='javascript: $( this ).attr("src", "static/prefstore_extension.png");'
						onmouseout='javascript: $( this ).attr("src", "static/prefstore_extension_blue.png");'
					/>
				</a>
			</div>
		</div>

		<div style="width:300px; margin-bottom:25;">
			<div class="instruction-header">
				Step 2.
			</div>
			<div class="instruction-description">
				Log into the Prefstore service, 
				& register an account (the top right button in the menu...)
			</div>
		</div>
		<div style="width:300px; margin-bottom:25;">
			<div class="instruction-header">
				Step 3.
			</div>
			<div class="instruction-description">
				That's it. As you surf the web, your private
				model will begin to form. A distillation of each page you surft
				is added to your global model.
			</div>
		</div>
	</div>


	<!---------------------------------------------------------------- 
		SUMMARY SECTION
	------------------------------------------------------------------>
	%if user:
	<div style="margin-left:530px; font-family:georgia; border:0px dotted #cccccc; width:380px;">
		Welcome back		
	</div>	
	%end
</div>

<!-- FOOTER ------------------------------------------------------------------>
%include footer