<html>
<head>
<title>Prefstore - Word Cloud</title>

<link rel="stylesheet" type="text/css" href="./static/layout.css" /> 
<script type="text/javascript" src="./static/jquery-1.6.min.js"></script> 

<script>

	
	$( document ).ready( function() {
		$( 'div.menu_button' ).mouseover(function() {
			$(this).css( 'cursor', 'hand' );
            $( this ).addClass( "menu_button_selected" );
			var kids = $(this).children();
			$( kids[ 0 ] ).addClass( "page-name-selected" );
			$( kids[ 1 ] ).addClass( "page-description-selected" );
		});

		$( 'div.menu_button' ).mouseout(function() {
			$(this).css( 'cursor', 'arrow' );
            $( this ).removeClass( "menu_button_selected" );
			var kids = $(this).children();
			$( kids[ 0 ] ).removeClass( "page-name-selected" );
			$( kids[ 1 ] ).removeClass( "page-description-selected" );
		});

		$( 'div.menu_button' ).click( function() {
			self.parent.location = "{{REALM}}/" + $( this ).attr('id');
		});

	});
</script>

</head>


<body>
<div class="top">
	<div class="header">
		<div class="logo">
			<img src="./static/dwlogofull.png"/>
		</div>
		
		%if user:
		<div id="logout" class="menu_button">
			<span class="top-menu-item">LOGOUT</span>
		</div>
		%else:
		<div id="login" class="menu_button">
			<span class="top-menu-item">LOGIN</span>
			<span class="menu-description">startup here</span></a> 
		</div>
		%end

		<div id="audit" class="menu_button">
			<span class="top-menu-item">AUDIT</span>
			<span class="menu-description">interactions</span></a> 
		</div>
		<div id="visualize"  class="menu_button">
			<span class="top-menu-item">VISUALIZE</span>
			<span class="menu-description">pretty pics</span></a> 
		</div>
		<div id="feed" class="menu_button">
			<span class="top-menu-item">DATA FEED</span>
			<span class="menu-description">your updates</span></a> 
		</div>
		<div id="summary" class="menu_button">
			<span class="top-menu-item">SUMMARY</span>
			<span class="menu-description">your dataware</span></a> 
		</div>
		<div id="home" class="menu_button">
			<span class="top-menu-item">HOME</span>
			<span class="menu-description">welcome</span></a> 
		</div>
	</div>
