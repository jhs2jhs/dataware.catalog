<!-- HEADER ------------------------------------------------------------------>
%include header

<!---------------------------------------------------------------- 
	PAGE SCRIPTS
------------------------------------------------------------------>
<script type="text/javascript"> 
	
	//-- create a word list from the different data categories
	var word_list = {{data}};
	var selected_term_list = new Array();
	
	//-- when the page is ready draw the word cloud
	$( document ).ready( function() {
		$( "#wordcloud" ).jQCloud(
			word_list[ "relevance" ],
			{ width: 800, height: 600 }
		)
	});
	
	
	/**
	 * function that will get called when a row is selected,
	 * which adds the chosen term to the selection box
	 */
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


	/**
	 * function that will reorder the wordcloud and the size of 
	 * its terms based on the category chosen.
	 */
	function visualize_by( type ) {

		//-- enable or disable the category choice links
		$( "#organized_by" ).children().each( 
			function() {
				str = $( this ).html()
				if ( str.indexOf( type ) > 0 )
					$( this ).html( str.replace("<a", "<x" ) )
				else 
					$( this ).html( str.replace("<x", "<a" ) )
			}	
		);

		//-- redraw the word cloud itself
		$( "#wordcloud" ).html("");
		$( "#wordcloud" ).jQCloud(
				word_list[ type ],
				{ width: 800, height: 600 }
		)
	}

</script>

<!---------------------------------------------------------------- 
	HEADER SECTION
------------------------------------------------------------------>
<div class="sub_header">
	<div class="page-name">VISUALIZE</div>
	<div class="page-description">A WORDCLOUD REPRESENTATION OF YOUR PREFSTORE MODEL</div>
</div>


<!---------------------------------------------------------------- 
	CONTENT SECTION
------------------------------------------------------------------>
<div class="main">

	<!---------------------------------------------------------------- 
		THE WORD CLOUD 
	------------------------------------------------------------------>
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

	<!---------------------------------------------------------------- 
		FILTER BOXES
	------------------------------------------------------------------>
	<div style="text-align:center; margin:34 0 0 20; float:left; border:1px solid #fafafa; width:175px;">

		<!-- SELECTED TERMS -------------------------------------------------------------->
		<div style="padding-top: 5px; height:23px; font-weight:bold; border:1px solid #dadada;"> 
			Selected Terms:
		</div>
		<div id="selectedList" style="min-height:50px; border:1px solid #eaeaea; background-color: #fafafa; padding:5px; font-size:11px;"> 
		</div>
		
		<!-- FILTER BOX ------------------------------------------------------------------>
		<div style="margin-top:15px; padding-top: 5px; height:23px; font-weight:bold; border:1px solid #dadada;"> 
			Fetch top 50 terms:
		</div>
		<div style="text-align:right; border:1px solid #eaeaea; background-color: #fafafa; padding:10 10 0 0;"> 
			<form name="filterForm" action="/visualize" method="GET" enctype="multipart/form-data">

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

				<span><a href="javascript:document.filterForm.submit();">Fetch</a></span>
			</form>
		</div>

		<!-- LARGEST WORD BOX------------------------------------------------------------->
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

<!-- FOOTER ------------------------------------------------------------------>
%include footer