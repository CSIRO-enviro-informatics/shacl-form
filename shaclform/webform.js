// Using val() on a checkbox always returns 'on' regardless of its actual value
// This function returns the correct value of an input without having to check for a checkbox every time
jQuery.fn.getValue = function() {
    if ($(this).attr('type') == 'checkbox')
        return $(this).is(':checked');
    else
        return $(this).val();
}

// To set the value of any input field or select field
jQuery.fn.setValue = function(value) {
    if ($(this).attr('type') == 'checkbox')
        $(this).prop('checked', value).change()
    else if ($(this).is('select'))
        $(this).children('[value="' + value + '"]').prop('selected', true).change()
    else if ($(this).attr('type') == 'radio')
        $(this).siblings(':radio[value="' + value + '"]').first().prop('checked', true).change()
    else
        $(this).val(value).change()
    return this
}

//Custom rules that can be used with any input type
$.validator.addMethod('data-equalTo', function(value, element, params) {
    var subject_value;
    var object_value;
    var object = $('[data-property-id=' + params + ']:not([disabled])');
    if (object.length == 0) return true;
    subject_value = $(element).getValue();
    object_value = $(object).getValue();
    if ($(element).attr('type') == 'checkbox')
        return subject_value == object_value;
    else
        return this.optional(element) || subject_value == object_value;
}, function(params, element) {
    return $.validator.format(
        'Must be equal to {0} ({1})',
        $('[data-property-id=' + $(element).attr('data-equalTo') + ']').attr('data-label'),
        $('[data-property-id=' + $(element).attr('data-equalTo') + ']').getValue()
    );
});
$.validator.addMethod('data-notEqualTo', function(value, element, params) {
    var subject_value;
    var object_value;
    var object = $('[data-property-id=' + params + ']:not([disabled])');
    if (object.length == 0) return true;
    subject_value = $(element).getValue();
    object_value = $(object).getValue();
    return this.optional(element) || subject_value != object_value;
}, function(params, element) {
    return $.validator.format(
        'Must not be equal to {0} ({1})',
        $('[data-property-id=' + $(element).attr('data-notEqualTo') + ']').attr('data-label'),
        $('[data-property-id=' + $(element).attr('data-notEqualTo') + ']').getValue()
    );
});
$.validator.addMethod('lessThan', function(value, element, params) {
    var subject_value;
    var object_value;
    var object = $('[data-property-id=' + params + ']:not([disabled])');
    if (object.length == 0) return true;
    subject_value = $(element).getValue();
    object_value = $(object).getValue();
    return this.optional(element) || subject_value < object_value;
}, function(params, element) {
    return $.validator.format(
        'Must be less than {0} ({1})',
        $('[data-property-id=' + $(element).attr('lessThan') + ']').attr('data-label'),
        $('[data-property-id=' + $(element).attr('lessThan') + ']').getValue()
    );
});
$.validator.addMethod('data-lessThanEqual', function(value, element, params) {
    var subject_value;
    var object_value;
    var object = $('[data-property-id=' + params + ']:not([disabled])');
    if (object.length == 0) return true;
    subject_value = $(element).getValue();
    object_value = $(object).getValue();
    return this.optional(element) || subject_value <= object_value;
}, function(params, element) {
    return $.validator.format(
        'Must be less than or equal to {0} ({1})',
        $('[data-property-id=' + $(element).attr('data-lessThanEqual') + ']').attr('data-label'),
        $('[data-property-id=' + $(element).attr('data-lessThanEqual') + ']').getValue()
    );
} );

// Used to automatically add custom rules to relevant elements. Disabled fields are not validated
$('#shacl-form').validate({
    ignore: '[disabled]',
    'data-equalTo': '[data-equalTo]',
    'data-notEqualTo': '[data-notEqualTo]',
    lessThan: '[lessThan]',
    'data-lessThanEqual': '[data-lessThanEqual]',
    errorPlacement: function(error, element) {
        if (element.attr('type') == 'radio')
            error.insertAfter(element.next().next());
        else
            error.insertAfter(element);
    }
});

//Apply pattern constraint to input field
var addPatternConstraint = function(element){
    var message = 'Must match pattern: /' +  $(element).attr('data-pattern') + '/'
    if ($(element).is('[flags]'))
        message += $(element).attr('flags');
    $(element).rules('add', {
        pattern: new RegExp($(element).attr('data-pattern'), $(element).attr('flags')),
        messages: { pattern: message }
    });
}

// Adds and removes entries when buttons are clicked
$('body').on('click', '.add-entry', function() {
    addEntry($(this).parent().children('.template').first())
});
$('body').on('click', '.remove-entry', function() {
    removeEntry($(this).parent().children('.template').first())
});

// Controls different parts of the form showing up depending on whether the user chooses to add a new node or link to an
// existing one.
$('#shacl-form').on('change', ':radio', function(){
    // Hide other options
    var nodeKindOptions = $(this).siblings('.nodeKindOption');
    nodeKindOptions.attr('hidden', 'hidden');
    // Disable other input fields
    nodeKindOptions.find('input, select').each(function(){
        $(this).attr('disabled', 'disabled');
    })
    // Reveal the selected option
    var value = $(this).val()
    var selectedOption = $(this).siblings('.nodeKindOption-' + $(this).val())
    selectedOption.removeAttr('hidden');
    //Enable revealed input fields
    selectedOption.find('input, select').each(function(){
        if ($(this).parents('.template').length == 0)
            $(this).removeAttr('disabled');
    })
})

// Checkboxes that are unchecked aren't submitted with the form
// The solution is for every checkbox to have a hidden partner with prefix 'unchecked:', which will submit if the main
// checkbox is unchecked
// This event ensures that the hidden checkbox is always checked when the main checkbox is unchecked, and the hidden
// checkbox is always unchecked when the main checkbox is checked
$('#shacl-form').on('change', ':checkbox', function(){
    if ($(this).is(':checked'))
        $('[name="Unchecked ' + $(this).attr('name') + '"]').removeAttr('checked');
    else
        $('[name="Unchecked ' + $(this).attr('name') + '"]').attr('checked', 'checked');
})

// Handles everything about adding an entry for a property
var addEntry = function(template, prefill_value, prefill_nodeKind) {
    var template_copy = template.clone()
    var entries = template.parent().children('.entries');
    var max_entries = template_copy.attr('data-max-entries');
    var min_entries = template_copy.attr('data-min-entries');
    var num_entries = entries.children().length;
    var root_id = template.children().find('[name]').attr('name').split(' ').pop();
    var id = root_id + "-" + entries.children().length;

    if (max_entries && num_entries >= max_entries) return; // Return if maximum entries is already reached

    // Update the ID through all children of this property
    template_copy.find('[name]').each(function(){
        $(this).attr('name', $(this).attr('name').replace(root_id, id));
    });

    // All entries below or at the minimum number of entries must be required
    if (min_entries != undefined && num_entries <= min_entries)
        template_copy.children().children().not('[type="checkbox"]').attr('required', 'required');

    // Append our prepared copy of the template to the entries
    var last_entry = entries.append(template_copy.html());
    num_entries++;

    // Apply prefill value if applicable
    if (prefill_value !== undefined && prefill_nodeKind !== undefined) {
        last_entry.find(':radio').filter('[name="NodeKind ' + id + '"]').setValue(prefill_nodeKind)
        var nodeKindContainer = last_entry.find('.nodeKindOption-' + prefill_nodeKind)
        if (nodeKindContainer.length == 0)
            last_entry.find('input, select').filter('[name=' + id + ']').first().setValue(prefill_value)
        else
            nodeKindContainer.find('input, select').filter('[name=' + id + ']').first().setValue(prefill_value)
    }

    // Enable input fields. Input fields are disabled when copied from the template
    // Apply pattern constraint if it should have one
    last_entry.find('input, select').each(function() {
        if ($(this).closest('.template').length == 0 && $(this).closest('.nodeKindOption').length == 0) {
            $(this).removeAttr('disabled');
            if ($(this).is('[data-pattern]'))
                addPatternConstraint($(this))
        }
    });

    // Control Add and Remove buttons
    if (num_entries > 0 && (min_entries == undefined || num_entries > min_entries))
        template.parent().children('.remove-entry').removeAttr('disabled');
    if (max_entries !== undefined && num_entries >= max_entries)
        template.parent().children('.add-entry').attr('disabled', 'disabled');
};

// Handles everything about removing an entry for a property
var removeEntry = function($template){
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
    if (num_entries <= min_entries || num_entries <= 0)
        $template.parent().children('.remove-entry').attr('disabled', 'disabled');
};

// Adds minimum number of fields when form is loaded
try {
    var prefill = JSON.parse($('#shacl-form-prefill').html());
} catch(err) {
    var prefill = []
}
$($('.template').get().reverse()).each(function(){
    var min_entries = $(this).attr('data-min-entries');
    var max_entries = $(this).attr('data-max-entries');
    var property_id = $(this).find('[name]').first().attr('name').split(' ').pop();
    for (i = 0; i < prefill.length; i++ ) {
        if (prefill[i]['id'] == property_id)
            var entries = prefill[i]['entries']
    }
    var num_entries = 0
    if (entries == undefined || entries.length < min_entries)
        num_entries = min_entries
    else if (entries.length > max_entries)
        num_entries = max_entries
    else
        num_entries = entries.length
    for (i = 0; i < num_entries; i++) {
        if (entries !== undefined && entries.length >= i) {
            var prefill_value = entries[i]['value']
            var prefill_nodeKind = entries[i]['nodeKind']
        }
        addEntry($(this), prefill_value, prefill_nodeKind);
    }
});