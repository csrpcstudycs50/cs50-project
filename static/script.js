// ADD INGREDIENT ROW
function addIngerdientRow()
{
    const container = document.getElementById("ingredients");

    const newRowHTML = `
                    <div name="ingredient group" class="input-group">
                    
                    <!--Name-->
                    <div class="form-floating mb-3">
                        <input type="text" class="form-control" id="floatingInput" name="ingredient_name" placeholder="eg.,flour" required>
                        <label for="floatingInput">Name</label>                       
                    </div>

                    <!--Amount-->
                    <div class="form-floating mb-3">
                    <input type="number" class="form-control" id="floatingInput" setp="0.01" name="ingredient_amount" placeholder="eg.,2." required>
                        <label for="floatingInput">Amount</label>
                    </div>

                    <!--unit of measure-->
                    <div class="form-floating">
                        <select class="form-select" name="unit" id="floatingSelect" aria-label="Floating label select example">
                            <!-- Weight / Mass -->
                            <option value="g" SELECTED>g</option>
                            <option value="kg">kg</option>
                            <option value="mg">mg</option>
                            <option value="oz">oz</option>
                            <option value="lb">lb</option>

                            <!-- Volume (Metric) -->
                            <option value="ml">ml</option>
                            <option value="l">l</option>

                            <!-- Volume (US / Imperial Standard) -->
                            <option value="tsp">tsp</option>
                            <option value="tbsp">tbsp</option>
                            <option value="fl oz">fl oz</option>
                            <option value="cup">cup</option>
                            <option value="pt">pt</option>

                            <!-- Whole Units & Counts -->
                            <option value="piece">piece</option>
                            <option value="whole">whole</option>
                            <option value="slice">slice</option>
                            <option value="clove">clove</option>
                            <option value="can">can</option>
                            <option value="package">package</option>

                            <!-- Culinary / Informal Measures -->
                            <option value="pinch">pinch</option>
                            <option value="dash">dash</option>
                            <option value="handful">handful</option>
                            <option value="bunch">bunch</option>
                            <option value="drop">drop</option>
                        </select>
                        <label for="floatingSelect">unit of measure</label>
                    </div>

                    <!--REMOVE button-->                    
                    <button class="btn btn-outline-danger input-group-text red mb-3" name="remove_ingredient" type="button">X</button>
                    
                </div>
    `;

    container.insertAdjacentHTML("beforeend", newRowHTML);
}

// WHEN ADD INGREDIENT BUTTON PRESSED
document.addEventListener("DOMContentLoaded",function(){
    const addIngredientBtn = document.getElementById("addIngredient");
    if (addIngredientBtn){
        addIngredientBtn.addEventListener("click",addIngerdientRow);
    }
});    

// WHEN REMOVE INGREDIENT BUTTON PRESSED
const ingredients = document.getElementById("ingredients");
if (ingredients){
    ingredients.addEventListener("click", function (event) {
    if (event.target && event.target.classList.contains("btn-outline-danger")) {
        event.target.closest(".input-group").remove();
    }
});
}




    
