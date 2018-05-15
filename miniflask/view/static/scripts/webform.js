//Custom rules that can be used with any input type
$.validator.addMethod("data-equalTo", function(value, element, params) {
    var subject_value;
    var object_value;
    var object = $("[data-property-id=" + params + "]:not([disabled])");
    if (object.length == 0) return true;
    if ($(element).attr("type") == "checkbox")
        subject_value = $(element).is(":checked");
    else
        subject_value = $(element).val();
    if (object.attr("type") == "checkbox")
        object_value = object.is(":checked");
    else
        object_value = object.val();
    return this.optional(element) || subject_value == object_value;
}, "Message" );
$.validator.addMethod("data-notEqualTo", function(value, element, params) {
    var subject_value;
    var object_value;
    var object = $("[data-property-id=" + params + "]:not([disabled])");
    if (object.length == 0) return true;
    if ($(element).attr("type") == "checkbox")
        subject_value = $(element).is(":checked");
    else
        subject_value = $(element).val();
    if (object.attr("type") == "checkbox")
        object_value = object.is(":checked");
    else
        object_value = object.val();
    return this.optional(element) || subject_value != object_value;
}, "Message" );
$.validator.addMethod("lessThan", function(value, element, params) {
    var subject_value;
    var object_value;
    var object = $("[data-property-id=" + params + "]:not([disabled])");
    if (object.length == 0) return true;
    if ($(element).attr("type") == "checkbox")
        subject_value = $(element).is(":checked");
    else
        subject_value = $(element).val();
    if (object.attr("type") == "checkbox")
        object_value = object.is(":checked");
    else
        object_value = object.val();
    return this.optional(element) || subject_value < object_value;
}, "Message" );
$.validator.addMethod("data-lessThanEqual", function(value, element, params) {
    var subject_value;
    var object_value;
    var object = $("[data-property-id=" + params + "]:not([disabled])");
    if (object.length == 0) return true;
    if ($(element).attr("type") == "checkbox")
        subject_value = $(element).is(":checked");
    else
        subject_value = $(element).val();
    if (object.attr("type") == "checkbox")
        object_value = object.is(":checked");
    else
        object_value = object.val();
    return this.optional(element) || subject_value <= object_value;
}, "Message" );

// Used to automatically add custom rules to relevant elements. Disabled fields are not validated
$("#form").validate({
    ignore: ":input[disabled]",
    "data-equalTo": ":input[data-equalTo]",
    "data-notEqualTo": ":input[data-notEqualTo]",
    lessThan: ":input[lessThan]",
    "data-lessThanEqual": ":input[data-lessThanEqual]",
    pattern: ":input[pattern]"
});

// Sets the message for equalTo validation
$(":input[data-equalTo]").each(function(index) {
    $(this).rules("add", {
        messages: {
            "data-equalTo": $.validator.format(
                "Must be equal to {0}",
                $("[data-property-id=" + $(this).attr("data-equalTo") + "]").attr("data-label")
            )
        }
    });
});

// Sets the message for notEqualTo validation
$(":input[data-notEqualTo]").each(function(index) {
    $(this).rules("add", {
        messages: {
            "data-notEqualTo": $.validator.format(
                "Must not be equal to {0}",
                $("[data-property-id=" + $(this).attr("data-notEqualTo") + "]").attr("data-label")
            )
        }
    });
});

// Sets the message for lessThan validation
$(":input[lessThan]").each(function(index) {
    $(this).rules("add", {
        messages: {
            lessThan: $.validator.format(
                "Must be less than {0}",
                $("[data-property-id=" + $(this).attr("lessThan") + "]").attr("data-label")
            )
        }
    });
});
$(":input[data-lessThanEqual]").each(function(index) {
    $(this).rules("add", {
        messages: {
            "data-lessThanEqual": $.validator.format(
                "Must be less than or equal to {0}",
                $("[data-property-id=" + $(this).attr("data-lessThanEqual") + "]").attr("data-label")
            )
        }
    });
});

// Script for adding multiple entries for a property
$('body').on('click', '.add-entry', function() {
    addEntry($(this).parent().children('.template').first())
});
$('body').on('click', '.remove-entry', function() {
    removeEntry($(this).parent().children('.template').first())
});
// Handles everything about adding an entry for a property
var addEntry = function($template) {
    var template_copy = $template.clone()
    var entries = $template.parent().children('.entries');
    var max_entries = template_copy.attr('data-max-entries');
    var min_entries = template_copy.attr('data-min-entries');
    var num_entries = entries.children().length;
    var root_id = $template.children().children().attr('name');
    var id = root_id + "-" + entries.children().length;

    if (max_entries && num_entries >= max_entries) return; // Return if maximum entries is already reached
    // Assign the new ID for this entry
    template_copy.children().children().attr('name', id);
    // Update the ID through all children of this property
    template_copy.children().children().find('[name]').each(function(){
        $(this).attr('name', $(this).attr('name').replace(root_id, id));
    });
    // All entries below or at the minimum number of entries must be required
    if (min_entries != undefined && num_entries <= min_entries)
        template_copy.children().children().attr('required', 'required');
    // Append our prepared copy of the template to the entries
    entries.append(template_copy.html());
    num_entries++;
    // Enable input fields. Input fields are disabled when copied from the template
    console.log("stuff");
    if ($template.parents('.template').length == 0){
        entries.find('input, select').each(function(){
            if ($(this).parents('.template').length == 0)
                $(this).removeAttr('disabled');
        });
    }
    // Control Add and Remove buttons
    if (num_entries > 0 && (min_entries == undefined || num_entries > min_entries)) $template.parent().children('.remove-entry').removeAttr('disabled');
    if (max_entries !== undefined && num_entries >= max_entries) $template.parent().children('.add-entry').attr('disabled', 'disabled');
};
// Handles everything about removing an entry for a property
var removeEntry = function($template) {
    var template_copy = $template.clone()
    var entries = $template.parent().children('.entries');
    var min_entries = template_copy.attr('data-min-entries');
    var num_entries = entries.children().length;

    // Return if minimum entries is already reached
    if ((!min_entries && num_entries == 0) || num_entries <= min_entries) return;
    // Removing a property means that the Add button can be enabled again
    $template.parent().children('.add-entry').removeAttr('disabled');
    // Remove the last entry
    entries.children().last().remove();
    num_entries--;
    // Disable Remove button if we reach the minimum number of entries
    if (num_entries <= min_entries || num_entries <= 0) $template.parent().children('.remove-entry').attr('disabled', 'disabled');
};

// Adds minimum number of fields when form is loaded
$($('.template').get().reverse()).each(function(){
    var min_entries = $(this).attr('data-min-entries');
    for (i = 0; i < min_entries; i++) {
        addEntry($(this));
    }
});