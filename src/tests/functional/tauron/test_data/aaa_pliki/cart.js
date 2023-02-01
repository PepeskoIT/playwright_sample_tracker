CheckProductsQuantity = function()
{
    var options = {
        delivery_type_id: 1,
        delivery_form_id: 1,
        plus_val: 1,/* gdy dodajemy produkt = 1, gdy sprawdzamy cały koszyk = 0 */
    };

    var max_delivery_types_quantity = '';
    var max_delivery_forms_quantity = '';

    var max_delivery_type_quantity = 0;
    var max_delivery_form_quantity = 0;
    var products_quantity = 0;
    var products_quantity_delivery_form = 0 ;

    var get_products_quantity_by_delivery_form = function()
    {
        var sum = 0;
        $('.quantity_df_' + options.delivery_form_id).each(function(){
            sum = sum + parseInt($(this).val());
        });
        return parseInt(sum);
    }

    var get_products_quantity = function()
    {
        var sum = 0;
        $('input[name="quantity"]').each(function(){
            sum = sum + parseInt($(this).val());
        });
        return parseInt(sum);
    }

    var get_max_quantity = function(){

        return parseInt(max_delivery_types_quantity[options.delivery_type_id]);
    }

    var get_max_delivery_form_quantity = function(){

        return parseInt(max_delivery_forms_quantity[options.delivery_form_id]);
    }
    
    var get_plus_val = function(){

        return parseInt(options.plus_val);
    }
    
    var set_cart_data = function(){
        
        if (max_delivery_types_quantity == '' || max_delivery_forms_quantity == '')
        {
            $.ajax({
                url: '/frontend/index/ajaxGetCartData',
                type: "GET",
                cache: false,   // MSIE cache'owal wyniki, a tego nie chcemy
                dataType: "json",
                success: function (data) {
                    
                    max_delivery_types_quantity = data.max_delivery_types_quantity;
                    max_delivery_forms_quantity = data.max_delivery_forms_quantity;
                    
                }
            });
        }
        
    }
    
    var set_options = function(_options){
        
        $.extend(options, _options);
        
        max_delivery_type_quantity = get_max_quantity();
        max_delivery_form_quantity = get_max_delivery_form_quantity();

        products_quantity = get_products_quantity();
        products_quantity_delivery_form = get_products_quantity_by_delivery_form();
    }
        
    var check = function()
    {

        if (parseInt(max_delivery_type_quantity) > 0 || max_delivery_form_quantity > 0)
        {

            if((get_plus_val() + products_quantity) > max_delivery_type_quantity || (get_plus_val() + products_quantity_delivery_form ) > max_delivery_form_quantity)
            {
                if ((get_plus_val() + products_quantity) > max_delivery_type_quantity) {
                    swal('Osiągnięto maksymalną ilość', 'Dla wybranego typu dostawy nie można zamówić więcej niż ' + max_delivery_type_quantity + ' sztuk');
                }

                if ((get_plus_val() + products_quantity_delivery_form ) > max_delivery_form_quantity) {
                    swal('Osiągnięto maksymalną ilość', 'Dla wybranego sposobu dostawy nie można zamówić więcej niż ' + max_delivery_form_quantity + ' sztuk');
                }
                //event.preventDefault();
                return false;
            }
        }
        /*else{
            swal('Wybierz sposób dostawy', 'proszę kliknąć przycisk "Wybieram" i określić sposób dostawy dla zamówienia');
            event.preventDefault();
            return false;
        }*/

        return true;
    };
    

    var init = function(){
        
        set_cart_data();
    };

    init();

    return {
        check : check,
        set_options: set_options        
    }
};

CanChangeDelivery = function(product_id)
{
    var product_id = product_id;
    var product_delivety_list = '';
    
    var set_products_delivery = function(){
       
        if (product_delivety_list == '')
        {
            $.ajax({
                url: '/frontend/index/ajaxGetCartProductsDelivery',
                type: "POST",
                data: {product_id: product_id},
                cache: false,   // MSIE cache'owal wyniki, a tego nie chcemy
                dataType: "json",
                success: function (data) {
                    if (data){
                        product_delivety_list = data;
                    }
                }
            });
        }
    }
    
    var check = function(delivery_type_id){
        
        var result = true;
        if (product_delivety_list == '')
        {
            swal({
                html: 'Brak ustawionych typów dostawy dla produktu',
                type: 'error'
            });
            result = false;
            
            return result
        }
        
        $.each(product_delivety_list.products, function(key, val){
            console.log(val);
            if (typeof val.delivery_types[delivery_type_id] === 'undefined')
            {
                swal({
                    html: 'Produkt "'+ val.product.name +'" nie ma sposobu dostawy "'+ product_delivety_list.delivery_types[delivery_type_id] +'". <br> Usuń produkt z koszyka aby zmienić sposób dostawy.',
                    type: 'error'
                });
                
                result = false;
                
                return result;
            }
            
        });
        return result;
    };
    
    var init = function(){
        
        set_products_delivery();
    };

    init();
    
    return {
        check : check,
    }
}