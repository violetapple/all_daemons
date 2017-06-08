$(document).ready(function(){
                var buttons = document.getElementsByName("action"); 
                var checked = document.getElementById("check").checked
                for (var i = 0; i < buttons.length; i++) 
                    document.getElementById(buttons[i].id).disabled = !checked;
            });
            
            function saveCheckBox(checked) {
                var buttons = document.getElementsByName("action");    
                for (var i = 0; i < buttons.length; i++) 
                    document.getElementById(buttons[i].id).disabled = !checked;
                $.ajax({
                    url : '/save_checkbox',
                    type : 'POST',
                    dataType : 'JSON',
                    contentType : 'application/multipart',
                    data  : JSON.stringify({"checked" : checked}),
                    success : function(response, smth){ 
                        data = JSON.parse(response)
                        console.log("Success. Checkbox value updated")
                    },
                    error : function(result, status, error){
                        console.log(result)
                        console.log(status)
                        console.log(error)
                    }
                 });
                
            }
            
            function updateButtonState(id, name) { 
                tag = '#state_' + name
                $(tag).text("*")
                var actions = {"start" : false, "restart" : false, "stop" : false}
                if(id == "start")
                    actions["start"] = true
                else if (id == "stop")
                    actions["stop"] = true
                else if (id == "restart")
                    actions["restart"] = true
                actions["name"] = name
                $.ajax({
                    url : '/change_daemon',
                    type : 'POST',
                    dataType : 'JSON',
                    contentType : 'application/multipart',
                    data  : JSON.stringify(actions),
                    success : function(response, smth){                       
                        data = JSON.parse(response)
                        tag = '#state_' + data["name"]
                        $(tag).text(data["state"])
                        console.log("Success. JSON has been received.")
                    },
                    error : function(result, status, error){
                        console.log(result)
                        console.log(status)
                        console.log(error)
                    }
                 });
            }
