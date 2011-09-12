<html>
<head>
	<title>
		Prefstore - Word Cloud
	</title>

	<script type="text/javascript" src="http://www.google.com/jsapi">
	</script>
	
	<script type="text/javascript" src="./static/jquery-1.6.min.js">
	</script> 

	<title>jQCloud Demo</title> 
	<link rel="stylesheet" type="text/css" href="./static/jqcloud.css" /> 
	
	<script type="text/javascript" src="./static/jqcloud-0.2.4.js"></script> 
	<script type="text/javascript"> 
		
		
		var word_list = {{data}};
		var selected_term_list = new Array();
		
		$( document ).ready( function() {
			$( "#wordcloud" ).jQCloud(
				word_list[ "relevance" ],
				{ width: 800, height: 600 }
			)
		});
		
		function select( selection ) {
			
			index = selected_term_list.indexOf( selection );
			
			if (index == -1 )
				selected_term_list.push( selection );
			else
				selected_term_list.splice( index, 1 );

			str = ""
			for ( i=0; i<selected_term_list.length; i++ )
				str += selected_term_list[ i ] + "<br/>";

			$("#selectedList").html( str ); 
		}

		function visualize_by( type ) {

			$( "#organized_by" ).children().each( 
				function() {
					str = $( this ).html()
					if ( str.indexOf( type ) > 0 )
						$( this ).html( str.replace("<a", "<x" ) )
					else 
						$( this ).html( str.replace("<x", "<a" ) )
				}	
			);

			$( "#wordcloud" ).html("");
			$( "#wordcloud" ).jQCloud(
					word_list[ type ],
					{ width: 800, height: 600 }
			)
	
		}

    </script> 
    
	<style type="text/css"> 

		body {
			background: #fff;
			font-family: Helvetica, Arial, sans-serif;
		}
	
		#wordcloud {
			width: 800px;
			height: 500px;
		}

		#wordcloud span.w10, #wordcloud span.w9, #wordcloud span.w8, #wordcloud span.w7 {
			text-shadow: 0px 1px 1px #ccc;
		}

		#wordcloud span.w3, #wordcloud span.w2, #wordcloud span.w1 {
			text-shadow: 0px 1px 1px #fff;
		}

		a {
			color:#5555ff;
			font-size: 11px; 
		}

		a:hover {
			color:#999999;
		}
	</style> 
</head> 

<body style="font-family: georgia; font-size:12px;">
<div style="margin: auto; height:768px; border:1px dotted gray; width:1020px; text-align:middle; ">

	<div style="float:left; width:800px;">
		<div style="text-align:right; margin-top:15px; margin-bottom:5px; font-size:11px; vertical-align:bottom">
			{{message}}
		</div>
		<div  style="border:1px solid #dadada;">
			<div style="
				height:18px; 
				background-image:url('./static/titleBack.png');		
				font-size: 13px;
				padding:5px;
			">
			</div>
			<div id="wordcloud" style="margin-top:0px; width:800; background-color:#f7f7ff"></div>
			<div style="
				height:18px; 
				background-image:url('./static/titleBack.png');		
				font-size: 13px;
				padding:5px;
			">
			</div>
		</div>
	</div>


	<div style="text-align:center; margin:34 0 0 20; float:left; border:1px solid #fafafa; width:175px;">
		<div style="padding-top: 5px; height:23px; font-weight:bold; border:1px solid #dadada;"> 
			Selected Terms:
		</div>
		<div id="selectedList" style="min-height:50px; border:1px solid #eaeaea; background-color: #fafafa; padding:5px; font-size:11px;"> 
		</div>
		
		<div style="margin-top:15px; padding-top: 5px; height:23px; font-weight:bold; border:1px solid #dadada;"> 
			Fetch top 50 terms:
		</div>
		<div style="text-align:right; border:1px solid #eaeaea; background-color: #fafafa; padding:10 10 0 0;"> 
			<form name="filterForm" action="/word_cloud" method="GET" enctype="multipart/form-data">

				<select name="order_by" style="width:150px; font-size:11px;">
					%if order_by == 'total appearances':
					<option selected="selected" value="total appearances">by total appearances</option>
					%else:
					<option value="total appearances">by term appearances</option>
					%end

					%if order_by == 'doc appearances':
					<option selected="selected" value="doc appearances">by doc appearances</option>
					%else:
					<option value="doc appearances">by doc appearances</option>
					%end

					%if order_by == 'frequency':
					<option selected="selected" value="frequency">by appearances per doc</option>
					%else:
					<option value="frequency">by appearances per doc</option>
					%end

					%if order_by == 'web importance':
					<option selected="selected" value="web importance">by importance on web</option>
					%else:
					<option value="web importance">by importance on web</option>
					%end

					%if order_by == 'relevance':
					<option selected="selected" value="relevance">by relevance to you</option>
					%else:
					<option value="relevance">by relevance to you</option>
					%end
				</select><br/>

				<input type="hidden" name="type" value="filter"/>
				<span><a href="javascript:document.filterForm.submit();">Fetch</a></span>
			</form>
		</div>

		<div style="margin-top:15px; padding-top: 5px; height:23px; font-weight:bold; border:1px solid #dadada;"> 
			Largest Word is...
		</div>
		<div id="organized_by" style="font-size:11px; text-align:left; border:1px solid #eaeaea; background-color: #fafafa; padding:10 10 10 10;"> 
			<div><x href="javascript:visualize_by('relevance');">most relevant to you</a></div>
			<div><a href="javascript:visualize_by('total appearances');">most seen by you</a></div>
			<div><a href="javascript:visualize_by('doc appearances');">most docs appeared in</a></div>
			<div><a href="javascript:visualize_by('web importance');">most common on the web</a></div>
		</div>
	</div>


</div>
</body> 
</html> 
