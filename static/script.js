// Function to generate and append a new ingredient row to a target container
function addIngredientRow(container) {
    if (!container) return;

    // Generate a unique ID timestamp to keep Bootstrap floating labels working correctly
    const uniqueId = Date.now();

    const newRowHTML = `
        <div name="ingredient group" class="input-group mb-3 ingredient-row">
            
            <!-- Name -->
            <div class="form-floating">
                <input type="text" class="form-control" id="ing_name_${uniqueId}" name="ingredient_name" placeholder="e.g., flour" required>
                <label for="ing_name_${uniqueId}">Name</label>                       
            </div>

            <!-- Amount -->
            <div class="form-floating">
                <input type="number" class="form-control" id="ing_amount_${uniqueId}" step="0.01" name="ingredient_amount" placeholder="e.g., 2" required>
                <label for="ing_amount_${uniqueId}">Amount</label>
            </div>

            <!-- Unit of Measure -->
            <div class="form-floating">
                <select class="form-select" name="unit" id="ing_unit_${uniqueId}" aria-label="Unit of measure">
                    <!-- Weight / Mass -->
                    <option value="g" selected>g</option>
                    <option value="kg">kg</option>
                    <option value="mg">mg</option>
                    <option value="oz">oz</option>
                    <option value="lb">lb</option>

                    <!-- Volume (Metric) -->
                    <option value="ml">ml</option>
                    <option value="l">l</option>

                    <!-- Volume (US / Imperial) -->
                    <option value="tsp">tsp</option>
                    <option value="tbsp">tbsp</option>
                    <option value="fl oz">fl oz</option>
                    <option value="cup">cup</option>
                    <option value="pt">pt</option>

                    <!-- Counts -->
                    <option value="piece">piece</option>
                    <option value="whole">whole</option>
                    <option value="slice">slice</option>
                    <option value="clove">clove</option>
                    <option value="can">can</option>
                    <option value="package">package</option>

                    <!-- Culinary -->
                    <option value="pinch">pinch</option>
                    <option value="dash">dash</option>
                    <option value="handful">handful</option>
                    <option value="bunch">bunch</option>
                    <option value="drop">drop</option>
                </select>
                <label for="ing_unit_${uniqueId}">Unit</label>
            </div>

            <!-- REMOVE button -->                    
            <button class="btn btn-outline-danger input-group-text remove-ingredient-btn" type="button">X</button>
        </div>
    `;

    container.insertAdjacentHTML("beforeend", newRowHTML);
}

document.addEventListener("DOMContentLoaded", function () {

    // 1. ADD INGREDIENT BUTTON (add.html & index.html card edits)
    document.addEventListener("click", function (event) {
        // Match both static #addIngredient and inline card add buttons (.add-ingredient-edit-btn)
        if (event.target && (event.target.id === "addIngredient" || event.target.classList.contains("add-ingredient-edit-btn"))) {
            // Find nearest ingredient container (.ingredients-container)
            const card = event.target.closest(".card");
            const container = card 
                ? card.querySelector(".ingredients-container") 
                : document.getElementById("ingredients");

            addIngredientRow(container);
        }
    });

    // 2. REMOVE INGREDIENT BUTTON (Global Event Delegation)
    document.addEventListener("click", function (event) {
        if (event.target && (event.target.classList.contains("remove-ingredient-btn") || event.target.name === "remove_ingredient")) {
            const row = event.target.closest(".input-group");
            if (row) {
                row.remove();
            }
        }
    });

    // 3. TOGGLE CARD EDIT / DISPLAY MODES (index.html)
    document.querySelectorAll(".edit-btn").forEach(button => {
        button.addEventListener("click", function () {
            const card = this.closest(".card");
            card.querySelector(".card-display").classList.add("d-none");
            card.querySelector(".card-edit").classList.remove("d-none");
        });
    });

    document.querySelectorAll(".cancel-btn").forEach(button => {
        button.addEventListener("click", function () {
            const card = this.closest(".card");
            card.querySelector(".card-edit").classList.add("d-none");
            card.querySelector(".card-display").classList.remove("d-none");
        });
    });

});