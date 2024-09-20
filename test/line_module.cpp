#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <cmath>
#include <tuple>
#include <optional>
#include <vector>

namespace py = pybind11;

using Point = std::tuple<double, double>;
using Direction = std::tuple<double, double>;
using Restriction = std::optional<std::tuple<double, double>>;

#ifndef M_PI
    #define M_PI 3.14159265358979323846
#endif

class Line {
public:
    Point origin;
    Direction direction;
    Restriction _restr;

    Line(Point origin, Direction direction, Restriction restrict = std::nullopt)
        : origin(origin), _restr(restrict) {
        if (std::get<0>(direction) == 0) {
            direction = {std::get<0>(direction) + 0.001, std::get<1>(direction)};
        }
        if (std::get<1>(direction) == 0) {
            direction = {std::get<0>(direction), std::get<1>(direction) + 0.001};
        }
        this->direction = normalize(direction);
    }

    Point g(double t) const {
        double ix = std::get<0>(origin) + std::get<0>(direction) * t;
        double iy = std::get<1>(origin) + std::get<1>(direction) * t;
        return {ix, iy};
    }

    double h(double x) const {
        double t = (x - std::get<0>(origin)) / std::get<0>(direction);
        double y = std::get<1>(origin) + t * std::get<1>(direction);
        return y;
    }

    static Direction normalize(Direction v) {
        double length = std::sqrt(std::pow(std::get<0>(v), 2) + std::pow(std::get<1>(v), 2));
        return {std::get<0>(v) / length, std::get<1>(v) / length};
    }

    static Line from_angle(Point origin, double angle, Restriction restrict = std::nullopt) {
        Direction direction = {std::cos(angle), std::sin(angle)};
        return Line(origin, direction, restrict);
    }

    static Line from_points(Point a, Point b, Restriction restrict = std::nullopt) {
        Direction direction = {std::get<0>(b) - std::get<0>(a), std::get<1>(b) - std::get<1>(a)};
        return Line(a, direction, restrict);
    }

    bool check_restrict(double t) const {
        if (!_restr) {
            return true;
        }
        auto [min, max] = *_restr;
        return min <= t && t <= max;
    }

    bool check_other_restrict(double t, const Line& other) const {
        double ix = std::get<0>(origin) + std::get<0>(direction) * t;
        double iy = std::get<1>(origin) + std::get<1>(direction) * t;
        double dx = ix - std::get<0>(other.origin);
        double dy = iy - std::get<1>(other.origin);
        double dot = dx * std::get<0>(other.direction) + dy * std::get<1>(other.direction);
        return other.check_restrict(dot);
    }

    bool is_on(Point p) const {
        auto [px, py] = p;
        auto [ox, oy] = origin;
        auto [dx, dy] = direction;
        double v_x = px - ox;
        double v_y = py - oy;
        double v_len = std::sqrt(v_x * v_x + v_y * v_y);
        double cp_x = ox + dx * v_len;
        double cp_y = oy + dy * v_len;
        bool is_close = std::abs(cp_x - px) < 1e-6 && std::abs(cp_y - py) < 1e-6;
        double dot = v_x * dx + v_y * dy;
        return is_close && check_restrict(dot);
    }

    std::optional<Point> intersection(const Line& other) const {
        auto [dx, dy] = direction;
        auto [ex, ey] = other.direction;
        auto [ox, oy] = origin;
        auto [px, py] = other.origin;
        double det = dx * ey - dy * ex;
        if (std::abs(det) < 1e-6) {
            return std::nullopt;
        }
        double t = (ex * (oy - py) - ey * (ox - px)) / det;
        if (!(check_restrict(t) && check_other_restrict(t, other))) {
            return std::nullopt;
        }
        return Point{ox + dx * t, oy + dy * t};
    }

    Direction normal() const {
        double angle = std::atan2(std::get<1>(direction), std::get<0>(direction)) + M_PI / 2;
        return {std::cos(angle), std::sin(angle)};
    }

    double distance(Point point) const {
        auto proj = project(point);
        double dx = std::get<0>(point) - std::get<0>(proj);
        double dy = std::get<1>(point) - std::get<1>(proj);
        return std::sqrt(dx * dx + dy * dy);
    }

    Point project(Point point) const {
        auto [px, py] = point;
        auto [ox, oy] = origin;
        auto [dx, dy] = direction;
        double v_x = px - ox;
        double v_y = py - oy;
        double t = v_x * dx + v_y * dy;
        return {ox + dx * t, oy + dy * t};
    }

    std::vector<std::tuple<int, int>> blocks_along_line() const {
        std::vector<std::tuple<int, int>> blocks;
        int x0 = std::floor(std::get<0>(origin));
        int y0 = std::floor(std::get<1>(origin));
        
        double dx = std::get<0>(direction);
        double dy = std::get<1>(direction);
        int step_x = dx > 0 ? 1 : -1;
        int step_y = dy > 0 ? 1 : -1;

        double nbx = (step_x > 0 ? x0 + 1 : x0) - std::get<0>(origin);
        double nby = (step_y > 0 ? y0 + 1 : y0) - std::get<1>(origin);
        double t_max_x = dx != 0 ? nbx / dx : std::numeric_limits<double>::infinity();
        double t_max_y = dy != 0 ? nby / dy : std::numeric_limits<double>::infinity();
        double t_delta_x = dx != 0 ? 1 / std::abs(dx) : std::numeric_limits<double>::infinity();
        double t_delta_y = dy != 0 ? 1 / std::abs(dy) : std::numeric_limits<double>::infinity();

        blocks.emplace_back(x0, y0);
        double t = 0;
        while (true) {
            if (t_max_x < t_max_y) {
                x0 += step_x;
                t = t_max_x;
                t_max_x += t_delta_x;
            } else {
                y0 += step_y;
                t = t_max_y;
                t_max_y += t_delta_y;
            }

            if (!check_restrict(t)) {
                break;
            }

            blocks.emplace_back(x0, y0);
        }

        return blocks;
    }
};

PYBIND11_MODULE(line_module, m) {
    py::class_<Line>(m, "Line")
        .def(py::init<Point, Direction, Restriction>(),
             py::arg("origin"), py::arg("direction"), py::arg("restrict") = std::nullopt)
        .def("g", &Line::g)
        .def("h", &Line::h)
        .def_static("from_angle", &Line::from_angle)
        .def_static("from_points", &Line::from_points)
        .def("is_on", &Line::is_on)
        .def("intersection", &Line::intersection)
        .def("normal", &Line::normal)
        .def("distance", &Line::distance)
        .def("project", &Line::project)
        .def("blocks_along_line", &Line::blocks_along_line)
        .def_property_readonly("origin", [](const Line& l) { return l.origin; })
        .def_property_readonly("direction", [](const Line& l) { return l.direction; });
}