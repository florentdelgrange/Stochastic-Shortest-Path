let print a =
    let n = Array.length a in
    let m = Array.length a.(0) in
    for i = 0 to (n - 1) do
        for j = 0 to (m - 2) do
            Printf.printf "%f\t" a.(i).(j);
        done;
        Printf.printf "%f\n" a.(i).(m - 1);
    done

let print_column a =
    let n = Array.length a in
    for i = 0 to (n - 2) do
        Printf.printf "%f\t" a.(i);
    done;
    Printf.printf "%f\n" a.(n - 1)

let copy_matrix m =
    let l = Array.length m in
    if l = 0 then m
    else
        let result = Array.make l m.(0) in
        for i = 0 to l - 1 do
            result.(i) <- Array.copy m.(i)
        done;
        result


let switch_line a i j =
    let n = Array.length a in
    if i < n && j < n then
        let m = Array.length a.(i) in
        for k = 0 to (m - 1) do
            let tmp = a.(i).(k) in
            a.(i).(k) <- a.(j).(k);
            a.(j).(k) <- tmp
        done

let weak_pivot a b i n =
    let rec max_line a i n current_line current_max =
        if current_line >= n then
            current_max
        else if abs_float(a.(current_max).(i)) < abs_float(a.(current_line).(i))
            then max_line a i n (current_line + 1) (current_line)
        else
            max_line a i n (current_line + 1) (current_max) in
    let l_max = max_line a i n i i in
    if l_max > i then
        switch_line a i l_max;
        let tmp = b.(i) in
        b.(i) <- b.(l_max);
        b.(l_max) <- tmp

let echelon a b =
    let n = Array.length a in
    for i = 0 to (n - 1) do (* diagonale *)
        weak_pivot a b i n;
        if a.(i).(i) <> 0. then
        (
            for j = (i + 1) to (n - 1) do (* line below ith line*)
                let coef = a.(j).(i) /. a.(i).(i) in
                b.(j) <- b.(j) -. b.(i) *. coef;
                for k = (i) to (n - 1) do (* row *)
                    a.(j).(k) <- a.(j).(k) -. a.(i).(k) *. coef;
                done;
            done;
        )
    done

let rec is_inversible a n ?(i = 0) () =
    if i = n then
        true
    else if a.(i).(i) = 0. then
        false
    else
        is_inversible a n ~i:(i + 1) ()

let resolve a b =
    let n = Array.length a in
    let n_a = copy_matrix a in
    let n_b = Array.copy b in
    let rec sum_coef a line row sol =
        if row = line then
            0.
        else
            sol.(row) *. a.(line).(row) +. (sum_coef a line (row - 1) sol) in
    echelon n_a n_b;
    if is_inversible a n () then
        (* on a bien une solution *)
        let sol = Array.make n 0. in
        for i = 0 to (n-1) do
            let j = n - 1 - i in
            if i = 0 then
                sol.(j) <- n_b.(j) /. n_a.(j).(j)
            else
                sol.(j) <- (n_b.(j) -.(sum_coef n_a j (n - 1) sol)) /.
                            n_a.(j).(j);
        done;
        sol
    else
        failwith "There isn't exactly one solution."
