
export default {
    name: "ManageOffices",

    props: {
        get_all_offices_url: {
            type: String,
            required: true
        },
        openeditofficefunc: {
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
            pageName: 'Manage Offices',
            rows: [],
            columns: [
                { label: 'Office Name'}
            ],

        };
    },

    methods: {
        DeleteOffice(office_id){
            if (!confirm("Are you sure you want to delete this office? This action cannot be undone.")){
                return;
            }
            axios.post('/delete_an_office', {'office_id': office_id})
            .then(response => {
                if (response.data.status === "success"){
                
                    alert(response.data.message);
                } else {
                    alert(response.data.message);
                }
                this.get_all_offices();
            })
            .catch(error => {
                console.error("There was an error deleting the office:", error);
            });
        },
        async EditOffice(office_id){
            const formData = await this.openeditofficefunc();
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
            payload['office_id']=office_id;
            const url='/modify_office';
            axios.post(url, payload)
            .then(response => {
                if (response.data.status === "success"){
                    console.log(response.data.message);
                } else {
                    console.error("Failed to edit office:", response.data.message);
                }
                this.get_all_offices();
            })
            .catch(error => {
                console.error("There was an error editing the office:", error);
            });
            
        },

        get_all_offices(){

            axios.get(this.get_all_offices_url)
            .then(response => {
                this.rows = response.data.offices;
            })
            .catch(error => {
                console.error("There was an error fetching offices:", error);
            });
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
                    row.name
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
       this.get_all_offices();
     
    },
    template: `
        <div class="container-fluid">
            <h2>{{ pageName }}</h2>
            <div class="table-container">
                <div class="search-wrapper">
                    <input
                        type="text"
                        class="form-control"
                        placeholder="Search offices..."
                        v-model="searchQuery"
                        style="width: 250px;"
                    >
                </div>
                <div class="table-responsive">
                    <table class="table table-bordered table-hover">
                        <thead>
                            <tr>
                                <th>Office Name</th>
                                <th> Actions </th>
                            </tr>
                        </thead>
                        
                        <tbody>
                            <tr v-for="office in paginatedRows" :key="office.id">
                                <td>{{ office.name }}</td>

                                
                                <td class="action-icons">
                                    <a @click="EditOffice(office.id)" >
                                        <span class="mr-1 fa fa-pencil text-warning">
                                        </span>
                                    </a>
                                    <a @click="DeleteOffice(office.id)" class="delete-office-link">
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
