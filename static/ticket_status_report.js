// MyComponent.js
export default {
  name: "TicketStatusReport",

  props: {
    report_route_url: {
      type: String
    },
    make_excel_url: {
      type: String
    }
  },

  data() {
    return {
      statistics: null,
      loading: true,
      error: null,
    };
  },

  methods: {
      fetch_reports() {
           
        this.loading = true;
        this.error = null;

        axios.get(this.report_route_url)
          .then(response => {
              this.statistics = response.data;
          })
          .catch(err => {
            console.error(err);
            this.error = "Failed to load statistics.";
          })
          .finally(() => {
            this.loading = false;
          });
        },

        download_excel(){
          const request_url = this.make_excel_url;
          axios.get(request_url, {
            responseType: 'blob',
            }).then((response) => {
                const url = window.URL.createObjectURL(new Blob([response.data]));
                const link = document.createElement('a');
                let filename = "report.xlsx"; // fallback
                const disposition = response.headers["content-disposition"];

                if (disposition) {
                  const match = disposition.match(/filename\*?=(?:UTF-8''|")?([^"]+)/);
                  if (match && match[1]) {
                    filename = decodeURIComponent(match[1]);
                  }
                }
        
                link.href = url;
                link.setAttribute('download', filename);
                document.body.appendChild(link);
                link.click();
              });
        }
  },
  computed: {
    // Convert your JSON into an array Vue can iterate
    officeRows() {
      if (!this.statistics || !this.statistics.statistics_by_office_name) {
        return [];
      }
      const offices = this.statistics.statistics_by_office_name;

      return Object.entries(offices).map(([officeName, stats]) => ({
        officeName,
        attended_count: stats.attended_count,
        processed_count: stats.processed_count,
        total_count: stats.total_count,
        unattended_count: stats.unattended_count,
        waiting_count: stats.waiting_count
      }));
    }
  },
  mounted() {
    this.fetch_reports();  // Auto-load once
  },
  template: `
    <div class="row">
      <div class="col-xs-12">
        <h2 style="margin-top: 0;"> Reports </h2>

        <button class="btn btn-default btn-sm pull-right"
          @click="fetch_reports"
          v-if="!loading">
          Refresh
        </button>
        <button class="btn btn-default btn-sm pull-right"
          @click="download_excel"
          v-if="!loading">
          Download Excel
        </button>
           
      </div>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="alert alert-info" style="margin-top:10px;">
      Loading statistics…
    </div>

    <!-- Error -->
    <div v-if="error" class="alert alert-danger" style="margin-top:10px;">
      {{ error }}
    </div>

    <!-- No Data -->
    <div v-if="!loading && !error && officeRows.length === 0"
         class="alert alert-warning" style="margin-top:10px;">
      No statistics available.
    </div>

    <!-- Statistics Table -->
    <div v-if="officeRows.length" style="margin-top:15px;">
      <table class="table table-bordered table-striped">
        <thead>
          <tr class="active">
            <th>Office</th>
            <th class="text-right">Total</th>
            <th class="text-right">Processing</th>
            <th class="text-right">Processed</th>
            <th class="text-right">Pulled</th>
            <th class="text-right">Unpulled</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="office in officeRows" :key="office.officeName">
            <td><strong>{{ office.officeName }}</strong></td>
            <td class="text-right">{{office.total_count }}</td>
            <td class="text-right">{{ office.attended_count }}</td>
            <td class="text-right">{{ office.processed_count }}</td>
            <td class="text-right">{{ office.unattended_count }}</td>
            <td class="text-right">{{ office.waiting_count }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  `
};
