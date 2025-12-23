
export default {
    name: "TaskThresholds",

    props: {
        get_all_tasks_url:{
            type: String
        },
        update_task_threshold_url:{
            type: String
        },
        showToast: {
            type: Function,
            required: true
        }
    },

    data() {
        return {
            tasks: {},
            input_v_models: {}
    
        };
    },

    methods: {
        get_all_tasks(){
            axios.get(this.get_all_tasks_url).then(response => {

                this.tasks = response.data;
            }).catch(error => {
                console.error("Error fetching tasks: ", error);
            });
        },
        updateTaskThreshold(task_name, new_threshold){
          console.log("Updating threshold for ", task_name, " to ", new_threshold);
            axios.post(this.update_task_threshold_url, {
                task_name: task_name,
                new_threshold: new_threshold
            }).then(response => {
                this.showToast("Threshold updated successfully!", "success");
                this.get_all_tasks(); // Refresh the task list
            }).catch(error => {
                console.error("Error updating threshold: ", error);
                this.showToast("Failed to update threshold.", "error");
            });
          this.input_v_models[task_name] = '';
        }
    
    },
    computed: {
    
    },
    watch:{
   
    },
    mounted() {
        this.get_all_tasks();

        for (const key in this.tasks) {
            this.input_v_models[key] = '';
        }
    },
    template: `
            <div class="row">
        <div class="col-xs-12">
          <h2 style="margin-top: 0;"> Set Task Thresholds </h2>
        </div>
        
        <div v-if="tasks && Object.keys(tasks).length">
          
          <div class="col-md-6 col-12" v-if="tasks && Object.keys(tasks).length">
            <h4 class="mt-3">Task Table</h4>
            <div class="table-responsive">
              <table class="table table-bordered table-striped table-sm">
                <thead>
                  <tr>
                    <th>Task Name</th>
                    <th>Task Threshold</th>
                    <th>Update Threshold</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(value, label) in tasks" :key="label">
                 
                    <td>{{ value.name }}</td>
                    <td>{{ value.threshold }}</td>
                    <td>
                        <input type="number" v-model="input_v_models[value.name]" min="0" placeholder="Set Threshold">
                        <button class="btn btn-primary btn-sm" @click="updateTaskThreshold(value.name, input_v_models[value.name])">Update</button>
                    </td>
                 
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
        <div v-else class="col-xs-12">
            <p>No Tasks Available.</p>
        </div>
        

      </div>
     
    
    `
};
