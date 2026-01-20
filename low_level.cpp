#include <cmath>
#include <iostream>
#include <vector>

#include <cpr/cpr.h>
#include <nlohmann/json.hpp>

#include <Eigen/Dense>

using json = nlohmann::json;

static std::vector<std::vector<double>> eigen_to_vec2(const Eigen::MatrixXd& A) {
  std::vector<std::vector<double>> out(A.rows(), std::vector<double>(A.cols()));
  for (int i = 0; i < A.rows(); ++i) {
    for (int j = 0; j < A.cols(); ++j) {
      out[i][j] = A(i, j);
    }
  }
  return out;
}

static std::vector<double> eigen_to_vec1(const Eigen::VectorXd& b) {
  std::vector<double> out(b.size());
  for (int i = 0; i < b.size(); ++i) {
    out[i] = b(i);
  }
  return out;
}

static Eigen::VectorXd vec1_to_eigen(const std::vector<double>& v) {
  Eigen::VectorXd out(v.size());
  for (int i = 0; i < static_cast<int>(v.size()); ++i) {
    out(i) = v[i];
  }
  return out;
}

int main(int argc, char** argv) {
  std::string url = "http://127.0.0.1:8000/task";
  int n = 400;
  if (argc >= 2) {
    n = std::stoi(argv[1]);
  }

  // Génère Ax=b
  Eigen::MatrixXd A = Eigen::MatrixXd::Random(n, n);
  Eigen::VectorXd b = Eigen::VectorXd::Random(n);

  // JSON compatible avec Task.to_json()/from_json()
  json payload;
  payload["identifier"] = 0;
  payload["size"] = n;
  payload["time"] = nullptr;
  payload["a"] = eigen_to_vec2(A);
  payload["b"] = eigen_to_vec1(b);
  payload["x"] = nullptr;

  auto r = cpr::Post(cpr::Url{url},
                     cpr::Header{{"Content-Type", "application/json"}},
                     cpr::Body{payload.dump()});

  if (r.error) {
    std::cerr << "HTTP error: " << r.error.message << "\n";
    return 2;
  }
  if (r.status_code != 200) {
    std::cerr << "HTTP status: " << r.status_code << "\n";
    std::cerr << r.text << "\n";
    return 3;
  }

  json resp = json::parse(r.text);

  std::vector<double> xvec = resp["x"].get<std::vector<double>>();
  Eigen::VectorXd x = vec1_to_eigen(xvec);

  double resid = (A * x - b).norm();
  std::cout << "n=" << n << "  proxy_time=" << resp.value("time", 0.0)
            << "  residual_norm=" << resid << "\n";

  if (!std::isfinite(resid) || resid > 1e-6 * std::sqrt(static_cast<double>(n))) {
    std::cerr << "Residual too high -> maybe mismatch in JSON format.\n";
    return 1;
  }

  return 0;
}
