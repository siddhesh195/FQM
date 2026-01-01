
export default {
    name: "ManageTasks",

    props: {
        get_all_tasks_url: {
            type: String,
            required: true
        },
        openedittaskfunc: {
            type: Function,
            required: true
        }
    },

    data() {
        return {
            searchQuery: '',
            // pagination
            currentPage: 1,
            perPage: 5,
            pageName: 'Manage Tasks',
            rows: [],
            columns: [
                { label: 'Task Name'},
                { label: 'Hidden Status' },
                { label: 'Offices' },
            ],

        };
    },

    methods: {
        truncate(text, length = 30) {
            if (!text) return ''
            return text.length > length
            ? text.substring(0, length) + '...'
            : text
        },
        async EditTask(task_id){
            const formData = await this.openedittaskfunc();
            if (!formData) {
                return;
            }
            //skip unfilled fields
            const payload={};
            for (const key in formData){
                if (formData[key]){
                    payload[key]=formData[key];
                }
            }
            payload['task_id']=task_id;
            const url='/modify_task';
            axios.post(url, payload)
            .then(response => {
                if (response.data.status === "success"){
                    console.log(response.data.message);
                } else {
                    console.error("Failed to edit task:", response.data.message);
                }
                this.get_all_tasks();
            })
            .catch(error => {
                console.error("There was an error editing the task:", error);
            });
            
        },
        DeleteTask(task_id){
            if (!confirm("Are you sure you want to delete this task? This action cannot be undone.")){
                return;
            }

            axios.post('/delete_a_task', {'task_id': task_id})
            .then(response => {
                if (response.data.status === "success"){
                    alert(response.data.message);
                } else {
                    alert(response.data.message);
                }
                this.get_all_tasks();
            })
            .catch(error => {
                console.error("There was an error deleting the task:", error);
            });
        },

        get_all_tasks(){

            axios.get(this.get_all_tasks_url)
            .then(response => {
                this.rows = response.data.tasks;
            })
            .catch(error => {
                console.error("There was an error fetching tasks:", error);
            });
        },
        show_hidden_label(hidden_status){
            if (hidden_status){
                return "Is Hidden";
            }
            return "Not Hidden";
        },
        nextPage() {
            this.goToPage(this.currentPage + 1);
        },

        prevPage() {
            this.goToPage(this.currentPage - 1);
        },
        goToPage(page) {
            if (page < 1 || page > this.totalPages) return;
            this.currentPage = page;
        }
    
    },
    computed: {
        totalPages() {
            return this.rows.length === 0
            ? 1
            : Math.ceil(this.rows.length / this.perPage);
        },
        paginatedRows() {
            const start = (this.currentPage - 1) * this.perPage;
            const end   = start + this.perPage;
            return this.filteredRows.slice(start, end);
        },
        filteredRows() {
            // no search → return all rows
            if (!this.searchQuery) {
                return this.rows;
            }
            const q = this.searchQuery.toLowerCase();
            // filter rows based on search query
            return this.rows.filter(row => {
                return [
                    row.name,
                    row.hidden,
                    row.offices,
                    this.show_hidden_label(row.hidden)
                ] 
                .filter(v => v !== null && v !== undefined)
                .some(v => String(v).toLowerCase().includes(q));
            });
        }
    
    },
    watch:{
        searchQuery() {
            this.currentPage = 1; // Reset to first page on new search
        }
    },
    mounted() {
       this.get_all_tasks();
     
    },
    template: `
        <div class="container-fluid">
            <h2>{{ pageName }}</h2>
            <div class="table-container">
                <div class="search-wrapper">
                    <input
                        type="text"
                        class="form-control"
                        placeholder="Search tasks..."
                        v-model="searchQuery"
                        style="width: 250px;"
                    >
                </div>
                <div class="table-responsive">
                    <table class="table table-bordered table-hover">
                        <thead>
                            <tr>
                                <th>Task Name</th>
                                <th> Task Hidden Status</th>
                                <th> Task Offices</th>
                                <th> Actions </th>
                            </tr>
                        </thead>
                        
                        <tbody>
                            <tr v-for="task in paginatedRows" :key="task.id">
                                <td :title="task.name">
                                    {{ truncate(task.name, 25) }}
                                </td>
                                <td>{{ show_hidden_label(task.hidden) }}</td>

                                <!-- Scrollable cell -->
                                <td>
                                    <div class="office-scroll">
                                        <div v-for="office in task.offices" :key="office">
                                            {{ office }}
                                        </div>
                                    </div>
                                </td>
                                <td class="action-icons">
                                    <a @click="EditTask(task.id)" >
                                        <span class="mr-1 fa fa-pencil text-warning">
                                        </span>
                                    </a>
                                    <a @click="DeleteTask(task.id)" class="delete-task-link">
                                        <span class="mr-1 fa fa-trash text-danger">
                                        </span>
                                    </a>


                                </td>
                    
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>

            <!-- Pagination controls -->
            <nav aria-label="Page navigation" >
                <div class="pagination-wrapper">
                    <div class="page-info">
                        Page {{ currentPage }} of {{ totalPages }}
                    </div>

                    <ul class="pagination">
                        <li class="page-item" :class="{ disabled: currentPage === 1 }">
                            <button class="page-link" @click="prevPage" :disabled="currentPage === 1">
                                Prev
                            </button>
                        </li>

                        <li
                            class="page-item"
                            v-for="page in totalPages"
                            :key="page"
                            :class="{ active: page === currentPage }"
                        >
                            <button class="page-link" @click="goToPage(page)">
                                {{ page }}
                            </button>
                        </li>

                        <li class="page-item" :class="{ disabled: currentPage === totalPages }">
                            <button class="page-link" @click="nextPage" :disabled="currentPage === totalPages">
                                Next
                            </button>
                        </li>
                    </ul>
                </div>
            </nav>

        </div>
     
    `
};
