document.addEventListener('DOMContentLoaded', function() {
    // Initialize CKEditor for the description field
    CKEDITOR.replace('description');

    // Initialize jQuery UI slider for the condition field
    $("#slider-range").slider({
        range: "min",
        value: 5,
        min: 1,
        max: 10,
        slide: function(event, ui) {
            $("#condition").val(ui.value); // Update the hidden input for condition
        }
    });
    $("#condition").val($("#slider-range").slider("value")); // Set initial value

    // Initialize Tagify for the players field
    const playerTagify = new Tagify(document.querySelector('[name=players]'), {
        whitelist: [
            { value: '1', label: '1' },
            { value: '2', label: '2' },
            { value: '3', label: '3' },
            { value: '4', label: '4' },
            { value: '5', label: '5' },
            { value: '6', label: '6' },
            { value: '7', label: '7' },
            { value: '8', label: '8' },
            { value: '9', label: '9' },
            { value: '10', label: '10+' }
        ],
        enforceWhitelist: true,
        dropdown: {
            maxItems: 10,
            classname: "tagify__dropdown",
            enabled: 0,
            closeOnSelect: false
        }
    });

    // Initialize Tagify for the tags field
    const tagTagify = new Tagify(document.querySelector('[name=tags]'), {
        whitelist: whitelist_tags, // Use the whitelist_tags passed from the server
        dropdown: {
            maxItems: 20,
            classname: "tagify__dropdown",
            enabled: 0,
            closeOnSelect: false
        }
    });

    // Autofill button click handler for fetching data from BoardGameGeek
    $('#autofillBtn').click(function() {
        const bggUrl = $('#bgg_url').val();
        if (bggUrl) {
            $.ajax({
                url: autofill_url, // URL passed from the server
                method: "POST",
                data: { bgg_url: bggUrl },
                success: function(response) {
                    if (response.success) {
                        // Fill in the form fields with the fetched data
                        $('#name').val(response.name);
                        CKEDITOR.instances.description.setData(response.description);
                        const players = response.players.map(num => ({
                            value: num.toString(),
                            label: num === '10' ? '10+' : num.toString()
                        }));
                        playerTagify.addTags(players);
                    } else {
                        alert(response.error);
                    }
                },
                error: function() {
                    alert("An error occurred while fetching data from BGG.");
                }
            });
        } else {
            alert("Please enter a valid BoardGameGeek URL.");
        }
    });
});
