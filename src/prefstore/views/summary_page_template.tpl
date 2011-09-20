<!-- HEADER ------------------------------------------------------------------>
%include header user=user
<!---------------------------------------------------------------- 
	PAGE SCRIPTS
------------------------------------------------------------------>
<script type="text/javascript">
</script>


<!---------------------------------------------------------------- 
	HEADER SECTION
------------------------------------------------------------------>

<div class="sub_header">
	<div class="page-name">SUMMARY</div>
	<div class="page-description">SEE ALL YOUR DETAILS, AND CONNECT TO YOUR DATASPHERE</div>
</div>


<!---------------------------------------------------------------- 
	CONTENT SECTION
------------------------------------------------------------------>
<style>
.table_item {
	height:36px;
	display: block;
	vertical-align: middle;
}

.table_field_name {
	float:left; 
	font-size:20; 
	font-weight:bold; 
	color:#009cd2;
}

.table_field_value {
	float:left; 
	font-size:14; 
	font-weight:normal; 
	color:#555555; 
	padding: 4 4 4 10;
}

</style>
<div class="main">

	<div style="margin:20px auto; font-family:georgia; padding:15px; border:1px dotted #cccccc; width:400px;">
		
		<div style="border-bottom: 1px dotted #aaaaaa; margin-bottom:15px;" >
			<div style="float:left">
				<img src="./static/icon_person.png" style="width:60px">
			</div>
			<div style="margin-left:75px">
				<div class="table_item">
					<div class="table_field_name">Username:</div>
					<div class="table_field_value">{{user[ "screen_name" ]}}</div>
				</div>
				<div class="table_item">
					<div class="table_field_name">Email:</div>
					<div class="table_field_value">{{user[ "email" ]}}</div>
				</div>
			</div>
		</div>

		<div style="border-bottom: 1px dotted #aaaaaa; margin-bottom:15px;" >
			<div style="float:left">
				<img src="./static/icon_distill.png" style="width:60px">
			</div>
			<div style="margin-left:75px">
					<div class="table_item">
					<div class="table_field_name">First Registered:</div>
					<div class="table_field_value"> {{user[ "registered_str" ]}} </div>
				</div>

				<div class="table_item">
					<div class="table_field_name">Last Distillation:</div>
					<div class="table_field_value"> {{user[ "last_distill_str" ]}} </div>
				</div>
			</div>
		</div>

		<div style="border-bottom: 1px dotted #aaaaaa; margin-bottom:15px;" >
			<div style="float:left">
				<img src="./static/icon_cogs.png" style="width:60px">
			</div>
			<div style="margin-left:75px">
				<div class="table_item">
					<div class="table_field_name">Total Distillations:</div>
					<div class="table_field_value"> {{user[ "total_documents" ]}} </div>
				</div>

				<div class="table_item">
					<div class="table_field_name">Total Terms Parsed:</div>
					<div class="table_field_value"> {{user[ "total_term_appearances"]}} </div>
				</div>

				<div class="table_item">
					<div class="table_field_name">Unique Terms Parsed:</div>
					<div class="table_field_value"> {{user[ "total_term_appearances"]}} </div>
				</div>
			</div>
		</div>





		<div class="separator"></div>



		<div class="separator"></div>

	</div>	
</div>




<!-- FOOTER ------------------------------------------------------------------>
%include footer